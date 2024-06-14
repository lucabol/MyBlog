//const syntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight")
const eleventyNavigationPlugin = require("@11ty/eleventy-navigation")
const { DateTime } = require("luxon")
const pluginRss = require("@11ty/eleventy-plugin-rss")
const { inlineSource } = require('inline-source')
const markdownIt = require('markdown-it')
const markdownItAnchor = require('markdown-it-anchor')
const description = require('eleventy-plugin-description')
const typesetPlugin = require('eleventy-plugin-typeset')
const typeset = require('typeset')
const yaml = require("js-yaml")
const fs = require('fs')
const Image = require("@11ty/eleventy-img")
const mathjaxPlugin = require("eleventy-plugin-mathjax")

require('dotenv').config()

const   dev  = global.dev  = (process.env.ELEVENTY_ENV === 'development')

/* INLINE FAVICON */
/* from https://github.com/popeindustries/inline-source/issues/231 */

const RE_XML_TAG = /<\?xml.+?\?>\s+/g;

const ATTRIBUTE_BLACKLIST = [
  'href',
  'rel',
  'src',
  'data',
  'xmlns',
  'xmlns:xlink',
  'version',
  'baseprofile'
];

function getAttributeString(attributes, prefix, strict) {
  let str = '';

  for (const prop in attributes) {
    // Ignore blacklisted and prefixed attributes
    const include = strict
      ? prop.indexOf(prefix) != 0 && !ATTRIBUTE_BLACKLIST.includes(prop)
      : prop.indexOf(prefix) != 0;

    if (include) {
      str +=
        attributes[prop] === true
          ? ` ${prop}`
          : ` ${prop}="${attributes[prop]}"`;
    }
  }

  return str;
}

function favicon(source, context) {
  return new Promise(async (resolve) => {
    if (source.fileContent && !source.content && source.type == 'image/x-icon') {
      const attributeType = source.attributes.type;
      let strict = !source.errored;
      let sourceProp = 'src';
      let data, encoding;

      delete source.attributes.type;

      {
        data = Buffer.from(source.fileContent).toString('base64');
        encoding = 'base64';

        // Favicon
        if (source.tag == 'link') {
          source.attributes.type = attributeType;
          sourceProp = 'href';
          strict = false;
          delete source.attributes.href;
        }
      }

      const src = `data:image/${source.format};${encoding},${data}`;
      let attrs = getAttributeString(
        source.attributes,
        context.attribute,
        strict
      );

      attrs += ` ${sourceProp}="${src}"`;
      source.content = src;
      source.replace = `<${source.tag}${attrs}/>`;
    }

    resolve();
  });
};
/* ENDOF INLINE FAVICON */

const inlineFunc = async (content, outputPath) => {
    if (!String(outputPath).endsWith('.html')) return content

    return await inlineSource(content, {
        compress: false, /* comressing images breaks adding a fallback image inside the svg as discussed in https://css-tricks.com/a-complete-guide-to-svg-fallbacks/ */
        handlers: [favicon] /* inlines favicon */
    })
}

// minify HTML
const htmlmin = require('html-minifier')

const htmlminifyFunc = (content, outputPath = '.html') => {

  if (!String(outputPath).endsWith('.html')) return content;

  return htmlmin.minify(content, {
    useShortDoctype: true,
    removeComments: true,
    collapseWhitespace: true
  });

}

async function imageShortcode(src, alt, sizes) {
  let metadata = await Image(src, {
    widths: [null],
    formats: [null]
  });

  let imageAttributes = {
    alt,
    sizes,
    loading: "lazy",
    decoding: "async",
  };

  // You bet we throw an error on missing alt in `imageAttributes` (alt="" works okay)
  return Image.generateHTML(metadata, imageAttributes, {
    whitespaceMode: "inline"
  });
}

module.exports = function(eleventyConfig) {
    eleventyConfig.addNunjucksAsyncShortcode("image", imageShortcode)
    eleventyConfig.addLiquidShortcode("image", imageShortcode)
    eleventyConfig.addJavaScriptFunction("image", imageShortcode)

    eleventyConfig.setQuietMode(true)

    eleventyConfig.addLayoutAlias('post', 'post.njk')
    eleventyConfig.addPassthroughCopy("css")
    eleventyConfig.addPassthroughCopy("img")
    eleventyConfig.addPassthroughCopy("*.png")
    eleventyConfig.addPassthroughCopy("*.jpg")
    eleventyConfig.addPassthroughCopy("*.ico")
    eleventyConfig.addPassthroughCopy("*.svg")
    eleventyConfig.addPassthroughCopy("fonts")
    eleventyConfig.addPassthroughCopy("wp-content/")
    eleventyConfig.addPlugin(eleventyNavigationPlugin)
    eleventyConfig.addPlugin(pluginRss);

    eleventyConfig.addFilter("readableDate", dateObj => 
        DateTime.fromJSDate(dateObj, {zone: 'utc'}).toFormat("LLL yyyy"))

    eleventyConfig.addFilter('htmlDateString', (dateObj) => 
        DateTime.fromJSDate(dateObj, {zone: 'utc'}).toFormat('yyyy-LL-dd'))

    eleventyConfig.addFilter('yearFromDate', (dateObj) => 
        DateTime.fromJSDate(dateObj, {zone: 'utc'}).year)

    eleventyConfig.addCollection("posts", ca => ca.getFilteredByGlob("posts/*.md"))

    eleventyConfig.addWatchTarget('js', './js/')
    eleventyConfig.addWatchTarget('img', './img/')

    eleventyConfig.addTransform("inline", inlineFunc)

    // Removing minification to be nice to other readers
    //eleventyConfig.addTransform("htmlminify", htmlminifyFunc)

    eleventyConfig.addCollection("tagList", function(collection) {
        let tagSet = new Set();
        collection.getAll().forEach(function(item) {
            if( "tags" in item.data ) {
                let tags = item.data.tags;

                tags = tags.filter(function(item) {
                    switch(item) {
                        // this list should match the `filter` list in tags.njk
                        case "all":
                        case "nav":
                        case "post":
                        case "posts":
                        return false;
                    }

                    return true;
                });

                for (const tag of tags) {
                    tagSet.add(tag.toLowerCase());
                }
            }
        });

        return [...tagSet].sort();
    })
  
  eleventyConfig.setLibrary( 'md', markdownIt({
          html: true,
          linkify: true,
          typographer: true,
      }
  ).use(markdownItAnchor))

  // To get 404 page when debugging locally 
  eleventyConfig.setBrowserSyncConfig({
    callbacks: {
      ready: function(err, bs) {

        bs.addMiddleware("*", (req, res) => {
          const content_404 = fs.readFileSync('_site/404.html');
          // Provides the 404 content without redirect.
          res.write(content_404);
          // Add 404 http status code in request header.
          // res.writeHead(404, { "Content-Type": "text/html" });
          res.writeHead(404);
          res.end();
        });
      }
    }
  })
  // Excerpt, use as --> <p>{{ post.templateContent | excerpt }}</p>
  eleventyConfig.addFilter("excerpt", (post) => {
    const content = post.replace(/(<([^>]+)>)/gi, "");
    return content.substr(0, content.lastIndexOf(" ", 150)) + "...";
  })
  // Prevents title to have just one word on last line
  eleventyConfig.addFilter("addNbsp", (str) => {
    if (!str) {
      return;
    }
    let title = str.replace(/((.*)\s(.*))$/g, "$2&nbsp;$3");
    title = title.replace(/"(.*)"/g, '\\"$1\\"');
    return title;
  })

  eleventyConfig.addPlugin(description)
  eleventyConfig.addPlugin(typesetPlugin({only: 'p'}))
  eleventyConfig.addPlugin(mathjaxPlugin)

  eleventyConfig.addFilter("groupByYear", function(posts) {
    var map = new Map() 
    posts.forEach( p => {
      const year = DateTime.fromJSDate(p.date, {zone: 'utc'}).year
      p.year = year
      if(!map.has(year)) {
        map.set(year, [])
      }
      map.get(year).push(p)
    })
    return map
  })
  
  eleventyConfig.addDataExtension("yaml", contents => yaml.safeLoad(contents))
} 
