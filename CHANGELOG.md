

## 1.1.0

### Added
- Linux support: load the ALP shared library (`libalpXX.so`) instead of the Windows `.dll` when running on Linux
- Default `libDir` on Linux is `/usr/lib/x86_64-linux-gnu/` when not specified
- Support for ALP API versions 5.0 and 5.1 on Windows (`alp50.dll`, `alp51.dll`) and Linux (`libalp50.so`, `libalp51.so`)
- Windows auto-detection of `libDir` from the registry handles the `ALP-5.X API` folder name used by ALP 5.X

### Fixed
- **`SeqPutEx()` now works on 64-bit Linux.** Two C data-handling errors in the wrapper were hidden by the Windows ABI:
  1. **`tAlpLinePut` struct member type.** `alp.h` declares the members as `int32_t`, but the wrapper used `ct.c_long`. On 64-bit Linux (LP64) `c_long` is 8 bytes, so the struct was 40 bytes instead of 20; the library misread the members (`PicLoad` decoded as 0, so zero pictures were loaded) and `SeqPutEx` silently did nothing while returning `ALP_OK`. The members are now `ct.c_int32`. On Windows `c_long` is 32-bit, so the old code happened to work.
  2. **Struct passed by value.** `AlpSeqPutEx` expects `void *UserStructPtr`, but the struct was passed by value. This only worked by accident on the Windows x64 ABI, which passes large structs by hidden reference; on the Linux System V ABI it shifted the argument registers and the call returned `ALP_PARM_INVALID`. The struct is now passed with `ct.byref`.

  Verified on hardware: both full-frame (`LineOffset=0, LineLoad=0`) and partial-line `SeqPutEx` display correctly on Linux. The fix is correct on all platforms.

### Changed
- `winreg` is only imported on Windows, so the module can be imported on other platforms
- Unsupported OS now raises `OSError` after the library path is resolved; unsupported ALP version raises `ValueError` on both platforms
- README section renamed to "Copy the .dll/.so"
- Packaging moved from `setup.py` to `pyproject.toml` (PEP 621); install with `pip install .` or `pip install -e .`
- Dependencies reduced to `numpy` and `six` (the only modules imported); `matplotlib`, `scipy`, `numba` and `joblib` are no longer pulled in
- Python 2 is no longer supported by the packaging; `requires-python = ">=3.7"`

## 1.0.3


### Fixed
- Corrected typos ProjInquireEx where SequenceId what passerd where not needed (see [#30](https://github.com/wavefrontshaping/ALP4lib/issues/30))
- Corrected typo in AlpProjControlEx (see [#29](https://github.com/wavefrontshaping/ALP4lib/issues/29))
- Add temp variable for Python data format in SeqPut and SeqPutEx to keep data in memory (see [#28](https://github.com/wavefrontshaping/ALP4lib/issues/28))

## 1.0.2

### Fixed
- Correct import for ALP 4.2 dll
- Add path to support ALP 4.4 dll
- Remove unused argument from `img_to_bitplane()`
 
## 1.0.1

### Fixed
- Bug correction for `DevInquire()`

### Improved
- `img_to_bitplane()` optimized using `numpy.packbits()` (thanks Dorian)