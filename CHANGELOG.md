

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