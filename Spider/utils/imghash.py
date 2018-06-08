from PIL import Image
import numpy
from scipy.fftpack import dct

class ImageHash:
    # refer to https://github.com/JohannesBuchner/imagehash
    def __str__(self):
        arr=self.signature.flatten()
        bit_string = ''.join(str(b) for b in 1*arr)
        width = int(numpy.ceil(len(bit_string)>>2))
        return '{:0>{width}x}'.format(int(bit_string, 2), width=width)

    def __sub__(self, other):
        return numpy.count_nonzero(self.signature != other.signature)

    def __eq__(self, other):
        return numpy.array_equal(self.signature, other.signature)

    def __ne__(self, other):
        return not numpy.array_equal(self.signature, other.signature)

    def ahash(self,image, hash_size=8):
        """
        Average Hash computation
        Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        """
        if hash_size < 2:
            raise ValueError("Hash size must be greater than or equal to 2")
    
        # reduce size and complexity, then covert to grayscale
        image = image.resize((hash_size, hash_size), Image.ANTIALIAS).convert("L")  # ANTIALIAS，抗锯齿
        pixels = numpy.asarray(image) # pixels is an array of the pixel values, ranging from 0 (black) to 255 (white)
        avg = pixels.mean()  # <class 'numpy.float64'>
        self.signature = pixels > avg
    
    def phash(self,image, hash_size=8, highfreq_factor=4):
        """
        Perceptual Hash computation.
        Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        """
        if hash_size < 2:
            raise ValueError("Hash size must be greater than or equal to 2")
    
        img_size = hash_size * highfreq_factor
        image = image.resize((img_size, img_size), Image.ANTIALIAS).convert("L")
        pixels = numpy.asarray(image)
        dct_result = dct(dct(pixels, axis=0), axis=1)
        dctlowfreq = dct_result[:hash_size, :hash_size]
        med = numpy.median(dctlowfreq)
        self.signature = dctlowfreq > med
    
        '''
        # simple version
        img_size = hash_size * highfreq_factor
        image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
        pixels = numpy.asarray(image)
        dct_result = dct(pixels)
        dctlowfreq = dct_result[:hash_size, 1:hash_size+1]
        avg = dctlowfreq.mean()
        self.signature = dctlowfreq > avg
        '''
    
    def dhash(self,image, hash_size=8):
        """
        Difference Hash computation.
        following http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        """
        if hash_size < 2:
            raise ValueError("Hash size must be greater than or equal to 2")
    
        image = image.resize((hash_size + 1, hash_size), Image.ANTIALIAS).convert("L")      # resize(w, h), but numpy.array((h, w))
        pixels = numpy.asarray(image)
        self.signature = pixels[:, 1:] > pixels[:, :-1]     # compute differences between columns
