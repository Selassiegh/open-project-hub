# 🔐 Security Policy

Security is important to Open Project Hub.

We want projects shared here to be safe for contributors and users.

## � Reporting a Security Vulnerability

If you discover a security vulnerability in the Open Project Hub repository, please do not open a public GitHub issue with sensitive details.

Use GitHub's private security reporting features when available, or contact the repository maintainers directly.

When reporting a vulnerability, please include:

* A clear description of the vulnerability
* The affected file, project, or component
* Steps to reproduce the issue
* The potential impact
* Any suggested fix, if available

Please do not publicly disclose the vulnerability until it has been reviewed.

## 🔑 Never Commit Secrets

Do not commit:

* API keys
* Access tokens
* Passwords
* Private keys
* Wallet seed phrases
* Database credentials
* Authentication secrets
* `.env` files containing secrets
* Personal or confidential information

## ⚠️ If You Accidentally Expose a Secret

Immediately:

1. Revoke or rotate the secret.
2. Remove it from the repository.
3. Notify the maintainers.
4. Check Git history for previous exposure.

**Removing a secret from the latest commit does not necessarily remove it from Git history.**

## 🛡️ Project Security

Projects should not intentionally contain:

* Malware
* Credential stealers
* Ransomware
* Phishing functionality
* Unauthorized surveillance
* Backdoors
* Destructive code
* Other intentionally harmful software

Security research, educational projects, and defensive cybersecurity tools are welcome when clearly documented and intended for legitimate use.

## � Security Reviews

Submitted projects may be reviewed before being accepted.

A project may be rejected or removed if it presents a significant security risk or violates repository guidelines.

## 📦 Third-Party Dependencies

Contributors should keep dependencies reasonably up to date and avoid known vulnerable packages where practical.

## ⚡ Responsible Disclosure

We encourage responsible disclosure.

Please give maintainers reasonable time to investigate and address reported vulnerabilities before publicly sharing detailed exploit information.

## 📜 Scope

This security policy applies to the Open Project Hub repository and its official infrastructure.

Individual projects may have their own security policies.

---

**Build openly. Share responsibly. Keep the community safe. �**
