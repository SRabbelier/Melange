(function(){var b=function(){var a=window.melange;this.prototype=new a.templates._baseTemplate;this.prototype.constructor=a.templates._baseTemplate;a.templates._baseTemplate.apply(this,arguments);a=new google.search.CustomSearchControl(this.context.cse_key);a.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);a.draw("cse")};jQuery(function(){melange.loadGoogleApi("search","1",{language:"en"},b)})})();
