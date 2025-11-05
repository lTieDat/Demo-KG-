# Quick Reference: Environment & Configuration

## Directory Structure (Expected)

```
DoAn/
├── Web/                          # Main application (this folder)
│   ├── app.py                    # Main entry point
│   ├── config.yaml              # Configuration file
│   ├── dataset/                 # Dataset files
│   ├── saved/                   # Model checkpoints
│   ├── components/              # UI components
│   ├── services/                # Business logic services
│   ├── styles/                  # CSS styling
│   └── ...other files
│
└── RecBole/                      # RecBole library (sibling folder)
    ├── saved/                   # Pre-trained models
    ├── dataset/                 # Dataset files
    └── ...RecBole source files
```

## Running the Application

### From Web directory:
```bash
cd Web
streamlit run app.py
```

### With custom Ollama URL:
```bash
# Windows
set OLLAMA_URL=http://your-machine:11434
streamlit run app.py

# Linux/Mac
export OLLAMA_URL=http://your-machine:11434
streamlit run app.py
```

## Configuration Files

### config.yaml
Used by RecBole for model training/loading:
- `data_path: ../RecBole/dataset/` - Relative path to RecBole dataset
- `dataset: code-ptit-100k` - Dataset name
- `embedding_size: 32` - Model parameter

### .env.example
Template for environment variables (not automatically loaded, FYI only):
```
OLLAMA_URL=http://localhost:11434
MODEL_DIR=./saved
RECBOLE_DIR=../RecBole
```

## Key Configuration Variables in app.py

```python
# Automatically computed from file location
BASE_DIR = Path(__file__).parent              # Web/
MODEL_DIR = str(BASE_DIR / "saved")           # Web/saved
RECBOLE_BASE_DIR = Path(__file__).parent.parent / "RecBole"  # DoAn/RecBole
RECBOLE_MODEL_DIR = str(RECBOLE_BASE_DIR / "saved")          # DoAn/RecBole/saved
```

## Ollama Configuration

### Default Setting
- **Default URL:** `http://localhost:11434`
- **Models:** mistral, llama2, phi3:mini, codellama

### Override Methods (in priority order)
1. **UI Input Field** - Set in "Ollama URL" field in Giải Thích Bằng AI section
2. **Environment Variable** - Set `OLLAMA_URL` before running app
3. **Default Value** - Uses `http://localhost:11434`

### Start Ollama Server
```bash
# Pull a model (if not already downloaded)
ollama pull mistral

# Start server
ollama serve
```

## Relative Path Resolution

All paths are relative to Python file locations using `Path(__file__).parent`:

- **app.py** → points to `Web/` directory
- **test.py** → points to `Web/` directory  
- **item_utils.py** → points to `Web/` directory
- **components/** → points to `Web/` directory
- **services/** → points to `Web/` directory

## File Location Examples

### Model Loading
```
Web/
└── saved/
    └── KGCN-*.pth        (loads relative to app.py)
```

### Dataset Files
```
Web/
└── dataset/
    ├── code-ptit-100k.item
    ├── code-ptit-100k.user
    └── ...
```

### RecBole Location
```
DoAn/
├── Web/
└── RecBole/              (../RecBole from Web/)
    ├── saved/
    └── dataset/
```

## Troubleshooting

### "Model not found" error
- Check that `Web/saved/` directory exists with `.pth` files
- Verify `BASE_DIR` computation is correct: `print(f"Model dir: {MODEL_DIR}")`

### "Cannot connect to Ollama"
- Start Ollama: `ollama serve`
- Check URL is correct: default is `http://localhost:11434`
- Override URL in UI or via `OLLAMA_URL` environment variable

### "Dataset not found"
- Check `Web/dataset/` contains required `.item`, `.user`, etc. files
- Verify `config.yaml` has correct `data_path: ../RecBole/dataset/`

### "RecBole import error"
- Verify `DoAn/RecBole/` directory exists at parent level
- Check Python path: `sys.path.insert(0, str(RECBOLE_BASE_DIR))`
- Install RecBole: `pip install recbole`

## Notes for Developers

- **No hard-coded absolute paths** - All use `Path(__file__).parent`
- **Cross-platform compatible** - Works on Windows, macOS, Linux
- **Environment-agnostic** - Can run from any directory location
- **Configurable Ollama** - Set via environment variable or UI
- **Automatic RecBole detection** - Adds to sys.path only if exists

## Version Information

- Python: 3.8+
- Streamlit: Latest
- RecBole: Latest (installed via pip)
- Ollama: Any recent version with API support
