# Security Policy — ToolOps

## Supported Versions

| Version | Supported |
| :--- | :--- |
| 0.2.x | ✅ Active development |
| 0.1.x | ✅ Critical fixes only |
| < 0.1.0 | ❌ No longer supported |

## Reporting a Vulnerability

**Please do not open a public issue for security vulnerabilities.**

Instead, report privately to:

- **Email:** hedi.manai.pro@gmail.com
- **Subject:** `[ToolOps Security] <brief description>`

Include in your report:

1. **Description** — What the vulnerability is
2. **Impact** — What an attacker could achieve
3. **Reproduction steps** — How to trigger the vulnerability
4. **Affected versions** — Which ToolOps versions are impacted
5. **Suggested fix** (optional) — If you have one

## Response Timeline

| Phase | Timeline |
| :--- | :--- |
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 7 days |
| Fix released | Within 30 days (critical: 7 days) |
| Public disclosure | After fix is released |

## Security Best Practices for Users

1. **Keep ToolOps updated.** Security fixes are released in patch versions.
2. **Use SHA-256 hashed cache keys.** Sensitive data should never appear in plaintext cache keys. ToolOps v0.2.0+ hashes all cache keys automatically.
3. **Protect your PostgreSQL connection strings.** Never commit credentials to version control. Use environment variables.
4. **Validate inputs.** ToolOps decorators do not sanitize tool function inputs — that remains the responsibility of your tool implementation.
5. **Enable circuit breakers** for external API calls to prevent cascading failures.

## Known Security Considerations

- **Cache key leakage (pre-v0.2.0):** Cache keys were generated from plaintext argument serialization. In v0.2.0, all cache keys are SHA-256 hashed.
- **Log parameter exposure (pre-v0.2.0):** Tool arguments were logged in plaintext. In v0.2.0, sensitive parameters are masked automatically.
- **PostgreSQL tag invalidation:** Pre-v0.2.0 loaded all cache entries into memory for tag-based invalidation. Fixed in v0.2.0 with GIN index and server-side filtering.

## Attribution

Security fixes will be credited in the [CHANGELOG](CHANGELOG.md) unless the reporter requests anonymity.
