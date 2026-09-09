

## 1.1.0

### Added
- Linux support: load the ALP shared library (`libalpXX.so`) instead of the Windows `.dll` when running on Linux
- Default `libDir` on Linux is `/usr/lib/x86_64-linux-gnu/` when not specified
- Support for ALP API versions 5.0 and 5.1 on Linux (`libalp50.so`, `libalp51.so`)

### Changed
- `winreg` is only imported on Windows, so the module can be imported on other platforms
- Unsupported OS now raises `OSError` after the library path is resolved; unsupported ALP version raises `ValueError` on both platforms
- README section renamed to "Copy the .dll/.so"

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