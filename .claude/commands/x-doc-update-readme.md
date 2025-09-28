# x-update-readme.md
# Office Add-in README Generator

Generate or update the project's main README.md by pulling from documentation, analyzing the codebase, and incorporating Office Add-in project metadata.

## Instructions

You are a README generator. Your task is to create a comprehensive, professional README.md that serves as the perfect entry point to the project.

1. **Gather Information From Multiple Sources**:

   ### From `/docs` folder:
   - Project overview from `docs/index.md`
   - Installation steps from `docs/getting-started/installation.md`
   - Quick start from `docs/getting-started/quickstart.md`
   - Architecture summary from `docs/architecture/overview.md`
   - API overview from `docs/api/reference.md`

   ### From codebase analysis:
   - Tech stack (React version, TypeScript version, Office.js API version)
   - Key dependencies from `package.json`
   - Available Office Add-in components
   - Test coverage (if available)
   - Build configuration (webpack)

   ### From existing files:
   - BACKLOG.md - for roadmap/future features
   - manifest.xml - for Office Add-in configuration
   - package.json - for dependencies and scripts

2. **Generate README.md Structure**:

   ```markdown
   # Project Name

   > Brief, compelling project description (2-3 lines)

   ## 🚀 Features

   - ✨ Feature 1 (from app analysis)
   - 🔐 Feature 2
   - 📱 Feature 3
   - 🎯 Feature 4

   ## 📋 Prerequisites

   - Node.js 14.x or higher
   - Microsoft 365 subscription (for testing)
   - Excel desktop application or Excel Online
   - Office Add-in dev certificates (installed automatically)

   ## 🛠️ Installation

   ### Quick Start
   ```bash
   # Clone the repository
   git clone <repo-url>
   cd <project-name>

   # Install dependencies
   npm install

   # Start development server and sideload to Excel
   npm start

   # Or just start the webpack dev server
   npm run dev-server
   ```

   Visit https://localhost:3000 (dev server) or use sideloaded add-in in Excel

   ## 🏗️ Project Structure

   ```
   .
   ├── src/
   │   ├── taskpane/       # Main taskpane UI components
   │   ├── commands/       # Ribbon command handlers
   │   └── __tests__/      # Test files
   ├── docs/              # Project documentation
   ├── manifest.xml       # Office Add-in manifest
   └── webpack.config.js  # Build configuration
   ```

   ## 📖 Documentation

   Full documentation is available in the `/docs` folder.

   To view docs in your browser:
   ```bash
   ./docs/viewdocs.sh
   ```

   Or visit:
   - [Office.js API Documentation](docs/office-api/overview.md)
   - [Architecture Overview](docs/architecture/overview.md)
   - [Development Guide](docs/development/setup.md)

   ## 🧪 Testing

   ```bash
   # Run all tests
   npm test

   # Run tests in watch mode
   npm run test:watch

   # Run with coverage
   npm run test:coverage
   ```

   ## 🚀 Deployment

   See [Deployment Guide](docs/deployment/production.md) for detailed instructions.

   ### Office Store Deployment:
   ```bash
   # Build for production
   npm run build

   # Validate manifest
   npm run validate
   ```

   ## 🛠️ Built With

   - **Frontend**: React 18.x, TypeScript
   - **UI Framework**: Fluent UI v9
   - **Office Integration**: Office.js API
   - **Build Tool**: Webpack 5
   - **Development**: office-addin-debugging tools

   ## 📝 Office.js API Usage

   Basic Office.js API example:
   ```typescript
   // Write data to Excel
   await Excel.run(async (context) => {
     const sheet = context.workbook.worksheets.getActiveWorksheet();
     const range = sheet.getRange("A1");
     range.values = [["Hello, World!"]];
     await context.sync();
   });

   // Read data from Excel
   await Excel.run(async (context) => {
     const range = context.workbook.getSelectedRange();
     range.load("values");
     await context.sync();
     console.log(range.values);
   });
   ```

   See [Office.js API Documentation](docs/office-api/overview.md) for complete reference.

   ## 🤝 Contributing

   1. Fork the repository
   2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
   3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
   4. Push to the branch (`git push origin feature/AmazingFeature`)
   5. Open a Pull Request

   See [Development Conventions](docs/development/conventions.md) for coding standards.

   ## 📊 Status

   - 🟢 Production Ready
   - Test Coverage: X%
   - Latest Release: vX.X.X

   ## 🗺️ Roadmap

   From BACKLOG.md:
   - [ ] Upcoming feature 1
   - [ ] Upcoming feature 2
   - [ ] Performance improvements

   ## 📄 License

   This project is licensed under the [LICENSE_TYPE] License - see the [LICENSE](LICENSE) file for details.

   ## 👥 Team

   - Your Name - Initial work - [GitHub](https://github.com/yourusername)

   ## 🙏 Acknowledgments

   - Hat tip to anyone whose code was used
   - Inspiration
   - etc
   ```

3. **Smart Content Generation**:
   - Extract feature list from Django apps
   - Determine tech stack from imports and settings
   - Create meaningful project structure visualization
   - Pull actual API examples from docs
   - Include test commands based on test framework

4. **Keep it DRY**:
   - Link to docs instead of duplicating
   - Reference existing documentation
   - Keep README focused on getting started

5. **Update vs Regenerate**:
   - If README exists, preserve custom sections
   - Update auto-generated sections only
   - Keep manual additions (like team, acknowledgments)

## Special handling for $ARGUMENTS:
- `--full`: Complete regeneration (overwrites existing)
- `--update`: Update only auto-generated sections
- `--minimal`: Create a minimal README
- `--include-badges`: Add status badges (build, coverage, etc.)

## Sections to Auto-Update:
- Features (from app analysis)
- Tech stack (from codebase)
- Installation (from docs)
- Project structure (from file system)
- API examples (from docs)
- Testing commands (from project setup)

## Sections to Preserve:
- Custom descriptions
- Team information
- Acknowledgments
- Special notes
- License choice

Always create a README that makes developers want to use and contribute to the project!
