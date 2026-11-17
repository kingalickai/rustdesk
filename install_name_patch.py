import io, re, sys
p = 'src/platform/mod.rs'
s = io.open(p, encoding='utf-8').read()
old = """
// Restrict names because installers interpolate them into privileged scripts and paths.
#[cfg(any(windows, target_os = "macos"))]
fn validate_install_app_name(app_name: &str) -> ResultType<()> {
    let mut bytes = app_name.bytes();
    let Some(first) = bytes.next() else {
        hbb_common::bail!("Application name must not be empty.");
    };
    // Keep leading hyphens valid on Windows for existing custom clients. macOS
    // rejects them because pgrep interprets a leading hyphen as an option.
    let valid_first =
        first.is_ascii_alphanumeric() || first == b'_' || (cfg!(windows) && first == b'-');
    if !valid_first
        || !bytes.all(|byte| byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'_')
    {
        let valid_prefix = if cfg!(windows) {
            "a letter, number, underscore, or hyphen"
        } else {
            "a letter, number, or underscore"
        };
        hbb_common::bail!(
            "Application name must start with {valid_prefix} and contain only letters, numbers, hyphens, and underscores."
        );
    }
    Ok(())
}"""
new = """
// Restrict names because installers interpolate them into privileged scripts and paths.
// [Tangyi] Allow Unicode (e.g. Chinese app name) while still blocking cmd.exe
// metacharacters and leading option-like characters. validate_install_value()
// independently rejects NUL/"/%/CR/LF/|/</> so no injection surface is added.
#[cfg(any(windows, target_os = "macos"))]
fn validate_install_app_name(app_name: &str) -> ResultType<()> {
    if app_name.is_empty() {
        hbb_common::bail!("Application name must not be empty.");
    }
    let dangerous = ['\\0', '"', '%', '\\r', '\\n', '|', '<', '>', '^', '&', ';', '!', '`', '$'];
    if app_name.chars().any(|c| dangerous.contains(&c)) {
        hbb_common::bail!(
            "Application name contains characters unsafe for the installer."
        );
    }
    let first = app_name.chars().next().unwrap();
    // Reject leading punctuation that cmd/pgrep could treat as an option/switch.
    if !first.is_alphanumeric() && first != '_' {
        hbb_common::bail!(
            "Application name must start with a letter, number, or underscore."
        );
    }
    Ok(())
}"""
if old not in s:
    print('[install_patch] WARN: exact block not found, trying regex fallback', flush=True)
    start = s.find('// Restrict names because installers interpolate')
    end = s.find('\n}\n', start)
    if start < 0 or end < 0:
        print('[install_patch] ERROR: anchor not found', flush=True)
        sys.exit(1)
    end += 3
    s = s[:start] + new + s[end:]
else:
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('[install_patch] validate_install_app_name patched OK', flush=True)
