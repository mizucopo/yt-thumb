# Git Flow

## WHY
Adopt a simple branching strategy to balance parallel development and quality assurance in team collaboration.
Minimize impact on production while enabling independent feature development.

## WHAT
- main: Production (production-ready code)
- develop: Development (integration branch for features)
- feature/*: Features (branch from develop, merge to develop)
- release/*: Not used
- hotfix/*: Not used

## HOW
```bash
# Start feature development
git checkout develop && git pull
git checkout -b feature/<feature-name>

# Create pull request
gh pr create --base develop

# File operations
git mv <old-path> <new-path>  # Move files
git rm <path>                  # Delete files
```

## Documentation

### WHY
Maintain consistency between code and documentation so developers can work with accurate information.

### WHAT
- README.md: Project overview, setup instructions, usage guide
- Other docs: API specs, architecture explanations, etc.

### HOW
- Update related documentation when code changes affect users
- Document usage for new features in README
- Update relevant docs when interfaces change
- Split large docs into separate files in `docs/` folder
- Add links to split docs in README
