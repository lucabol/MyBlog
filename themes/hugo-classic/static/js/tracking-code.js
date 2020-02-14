const init = () => {

    // Load analytics.js
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    // Initialize the command queue in case analytics.js hasn't loaded yet.
    window.ga = window.ga || ((...args) => (ga.q = ga.q || []).push(args));

    ga('create', 'UA-133194891-1', 'auto');
    ga('set', 'transport', 'beacon');
    ga('send', 'pageview');
};

// Set up on onload event
window.addEventListener('load', init);