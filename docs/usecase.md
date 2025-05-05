# Using MS2MD: Local and Global Approaches

There are two main ways to use the MS2MD tool: directly from the cloned repository or as a globally installed command. Let me explain both approaches.

## Approach 1: Using MS2MD Locally from the Repository

This approach is useful for quick testing or if you prefer not to install the tool globally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ms2md.git
cd ms2md
```

### Step 2: Set Up the Directory Structure

Create input and output directories within the repository:

```bash
mkdir -p files/input files/output
```

### Step 3: Place Your DOCX Files

Copy your chapter files into the input directory:

```bash
cp /path/to/your/chapter1.docx files/input/
cp /path/to/your/chapter2.docx files/input/
# ... and so on for other chapters
```

### Step 4: Install Dependencies Locally

Using uv (recommended):

```bash
uv venv
uv pip install -r requirements.txt
```

Or using standard pip:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Run the Conversion

From the repository root directory:

```bash
# Using Python module syntax
python -m ms2md batch ./files/input ./files/output

# Or using the script directly
python scripts/ms2md batch ./files/input ./files/output
```

All your chapter files will be converted and placed in the `files/output` directory with the same filenames but with `.md` extensions.

## Approach 2: Installing MS2MD Globally

This approach allows you to use MS2MD from any directory on your system, similar to how you use git.

### Step 1: Install MS2MD Globally

Clone the repository and install it:

```bash
git clone https://github.com/yourusername/ms2md.git
cd ms2md
```

Choose one of the following installation methods:

**User installation (recommended):**
```bash
make install-user
# Or directly: pip install --user .
```

**System-wide installation:**
```bash
make install-system
# Or directly: sudo pip install .
```

**Development mode** (if you plan to modify the code):
```bash
make install-dev
# Or directly: pip install --user -e .
```

The `-e` flag installs in "editable" mode, which means you can update the repository and the changes will be reflected in the installed package.

> **Note**: Make sure your Python scripts directory is in your PATH. This is typically:
> - Linux/macOS: `~/.local/bin` (for `--user` installs) or `/usr/local/bin` (for system-wide installs)
> - Windows: `%APPDATA%\Python\Python3x\Scripts`
>
> You may need to add this to your PATH or restart your terminal after installation.

### Step 2: Verify the Installation

From any directory, you should now be able to run:

```bash
ms2md --version
```

This should display the version of MS2MD, confirming it's properly installed.

### Step 3: Use MS2MD from Any Directory

Now you can navigate to any directory containing your DOCX files and use MS2MD:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Create directories for your files
mkdir -p chapters markdown

# Copy your chapter files
cp /path/to/your/chapter*.docx chapters/

# Run the batch conversion
ms2md batch ./chapters ./markdown
```

### Step 4: Create a Configuration File (Optional)

For consistent settings across conversions, create a config.yaml file:

```bash
# Create a config file
cat > config.yaml << EOF
equations:
  inline_delimiters: ["$", "$"]
  display_delimiters: ["$$", "$$"]
images:
  extract_path: "./images"
  optimize: true
processing:
  fix_delimiters: true
  extract_images: true
  process_tables: true
EOF

# Use the config file with your conversion
ms2md batch ./chapters ./markdown --config ./config.yaml
```

## Additional Tips

1. **Processing Individual Files**: If you want to process just one file:
   ```bash
   ms2md convert chapter1.docx chapter1.md
   ```

2. **Fixing Delimiters in Existing Files**: If you already have Markdown files with incorrect delimiters:
   ```bash
   ms2md fix-delimiters chapter1.md
   ```

3. **Validating Equations**: To check if equations in a Markdown file are valid:
   ```bash
   ms2md validate chapter1.md
   ```

4. **Getting Help**: For more information about any command:
   ```bash
   ms2md --help
   ms2md convert --help
   ```

With either approach, you can efficiently convert your chapter files from Word to Markdown+LaTeX format, ready for further processing with tools like mdtexpdf.