// image minification
// delete _site/img to recreate minified images
const
  dest = './_site/img',

  fsp = require('fs').promises,
  imagemin = require('imagemin'),
  plugins = [
    require('imagemin-mozjpeg')(),
    require('imagemin-pngquant')({ strip: true }),
    require('imagemin-svgo')()
  ];

module.exports = class {

  data() {

    return {
      permalink: false,
      eleventyExcludeFromCollections: true
    };

  }

  // process all files
  async render() {

    // destination already exists?
    try {
      let dir = await fsp.stat(dest);
      if (dir.isDirectory()) return true;
    }
    catch(e){}

    // process images
    console.log('optimizing images');

    await imagemin(['img/*', '!img/*.js'], {
      destination: dest,
      plugins
    });

    return true;

  }
};
