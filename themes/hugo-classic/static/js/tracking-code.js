const init = () => {
  // Initialize the command queue in case analytics.js hasn't loaded yet.
  window.ga = window.ga || ((...args) => (ga.q = ga.q || []).push(args));

  ga('create', 'UA-133194891-1', 'auto');
  ga('set', 'transport', 'beacon');
  ga('send', 'pageview');
};

// Call init here. Alternatively, we could call it when we figured out the user is a legit one (i.e. first mouse move)
init();