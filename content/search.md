---
title: "Search Results"
sitemap:
  priority : 0.1
---
<section >
  <div >
    <form action="/search">
      <input id="search-query" name="s"/>
    </form>
    <div id="search-results">
     <h3>Matching pages</h3>
    </div>
  </div>
</section>
<!-- this template is sucked in by search.js and appended to the search-results div above. So editing here will adjust style -->
<script id="search-result-template" type="text/x-js-template">
    <div id="summary-${key}">
        <h3><a href="${link}">${title}</a></h3>
        <p>${snippet}</p>
        ${ isset tags }<p>Tags: ${tags}</p>${ end }
    </div>
</script>

<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/fuse.js/3.2.0/fuse.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/jquery.mark.min.js"></script>
<script src="/js/search.js"></script>