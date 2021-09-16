# Twitter_PFP_Randomizer
A configurable script that will rotate different parts of your twitter profile

Still very much a work in progress, made for personal use. 

This won't work unless you get your own keys for the Twitter API. Also, you'll need to set up the configuration files with your information and the paths for your images. There are blank / example configs in the templates directory. 

**Features:**
- Update your Twitter name via API
    * Add a random punctuation mark to the end of your name, with configurable weights
    * Pick a random line from a text file and append it to the end of your name

- Update your Twitter PFP via API
    * Recursively finds JPG, PNG, and GIF images stored in a configurable location
    * Define multiple pools of images that are pulled from different paths
    * Adjust the relative weight of different image pools 
    * Optional feature that prevents the same artist's image appearing twice in a row

- Update your Twitter bio via API
    * Not very much going on here, besides allowing you to update your bio to contain an artist credit for your PFP.

**Down the Line (maybe):**
- More contextual info to put in your bio
- Additional options for configuration
- Easier way to use this? Idk, I need to learn more about twitter auth 
