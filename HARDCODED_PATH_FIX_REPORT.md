# Hard-coded Path/URL Removal - Summary Report

## Overview
All hard-coded absolute paths and localhost URLs have been replaced with relative paths and configurable environment variables, making the application portable across different environments and machines.

## Changes Made

### 1. **app.py** ✅
**Status:** Fixed
- Replaced `RECBOLE_MODEL_DIR = r"E:\DoAn\RecBole\saved"` with relative path:
  ```python
  BASE_DIR = Path(__file__).parent
  RECBOLE_BASE_DIR = Path(__file__).parent.parent / "RecBole"
  RECBOLE_MODEL_DIR = str(RECBOLE_BASE_DIR / "saved")
  ```
- Uses `Path(__file__).parent` for cross-platform compatibility
- Conditionally adds RecBole to sys.path if directory exists

### 2. **components/ai_explanation.py** ✅
**Status:** Fixed
- Removed hard-coded `"http://localhost:11434"` from `st.text_input()`
- Now reads from session state with fallback to default:
  ```python
  default_url = st.session_state.get("ollama_url", "http://localhost:11434")
  base_url = st.text_input("Ollama URL:", default_url, key="global_ollama_url")
  st.session_state["ollama_url"] = base_url
  ```
- Removed emoji (🤖) from header

### 3. **llm_explainer.py** ✅
**Status:** Fixed
- Updated `OllamaExplainer.__init__()` to accept `base_url=None` parameter
- Now uses environment variable or default:
  ```python
  self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
  ```
- Allows override via `OLLAMA_URL` environment variable

### 4. **ollama_demo.py** ✅
**Status:** Fixed
- Updated `OllamaDemo.__init__()` to accept `base_url=None` parameter
- Now uses environment variable or default:
  ```python
  self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
  ```

### 5. **test.py** ✅
**Status:** Fixed
- Replaced hard-coded path `"E:/DoAn/RecBole/saved/KGCN-Apr-20-2025_11-17-38.pth"`
- Now uses relative paths with Path module:
  ```python
  BASE_DIR = Path(__file__).parent.parent
  RECBOLE_SAVED_DIR = BASE_DIR / "RecBole" / "saved"
  MODEL_PATH = RECBOLE_SAVED_DIR / MODEL_NAME
  ```
- Added path existence check before loading

### 6. **item_utils.py** ✅
**Status:** Fixed
- Removed hard-coded path `"e:/DoAn/Web/dataset/code-ptit-100k.item"`
- Now uses relative paths with Path module:
  ```python
  base_dir = Path(__file__).parent
  possible_paths = [
      base_dir / "dataset" / "code-ptit-100k.item",
      Path.cwd() / "dataset" / "code-ptit-100k.item",
      base_dir.parent / "Web" / "dataset" / "code-ptit-100k.item",
  ]
  ```
- Tries multiple path locations for flexibility

### 7. **config.yaml** ✅
**Status:** Fixed
- Replaced `data_path: E:/DoAn/RecBole/dataset/` with:
  ```yaml
  data_path: ../RecBole/dataset/
  ```
- Now uses relative path compatible with different directory structures

### 8. **readme.md** ✅
**Status:** Fixed
- Changed `cd E:\DoAn\demo` to `cd Web`
- Documentation now uses relative paths

### 9. **.env.example** ✅
**Status:** Created
New configuration template file created with:
```
OLLAMA_URL=http://localhost:11434
MODEL_DIR=./saved
RECBOLE_DIR=../RecBole
RECBOLE_DATASET=code-ptit-100k
```

## Files NOT Modified (No Hard-coding Found)

- **services/model_service.py**: Already receives paths from app.py (no direct hard-coding)
- **components/sidebar.py**: Uses relative paths from model_service (no direct hard-coding)
- All component files: Use paths from main app configuration

## Default Values vs Hard-coded Paths

**Default Values (ACCEPTABLE):**
- `OLLAMA_URL` defaults to `http://localhost:11434` (standard Ollama default)
- These can be overridden via:
  - UI input (ai_explanation.py)
  - Environment variables: `OLLAMA_URL`
  - Direct parameter passing

**Previously Hard-coded Paths (NOW FIXED):**
- ❌ `E:\DoAn\RecBole\saved` → ✅ `../RecBole/saved`
- ❌ `E:/DoAn/Web/dataset/code-ptit-100k.item` → ✅ `./dataset/code-ptit-100k.item`
- ❌ `E:\DoAn\demo` → ✅ `Web`

## Environment Variable Support

The application now supports configuration via environment variables:

```bash
# Set Ollama server URL
set OLLAMA_URL=http://your-server:11434

# Or for Linux/Mac:
export OLLAMA_URL=http://your-server:11434
```

## Cross-Platform Compatibility

- ✅ Uses `Path` module from `pathlib` for cross-platform paths
- ✅ All backslashes converted to forward slashes or Path objects
- ✅ Relative paths work on Windows, macOS, and Linux
- ✅ No Windows-specific path syntax

## Testing Recommendations

1. **Test Different Directories:**
   - Run app.py from Web/ directory
   - Run app.py from parent directory
   - Run app.py from completely different location

2. **Test Environment Variables:**
   ```bash
   set OLLAMA_URL=http://localhost:11434
   streamlit run app.py
   ```

3. **Test with Different Ollama Instances:**
   - Use default localhost
   - Change URL to different host/port via UI or env var
   - Verify connection test works

4. **Test Model Loading:**
   - Verify models load from relative ./saved directory
   - Check RecBole integration still works

## Remaining Notes

- Default `OLLAMA_URL` is still `http://localhost:11434` for backward compatibility
- This can be overridden in three ways:
  1. Environment variable: `OLLAMA_URL`
  2. UI input field in ai_explanation component
  3. Direct parameter when creating OllamaExplainer
- All critical absolute paths have been converted to relative paths
- Application is now portable across different machines and environments
