(function(){var a=window.melange;this.prototype=new a.templates._baseTemplate;this.prototype.constructor=a.templates._baseTemplate;a.templates._baseTemplate.apply(this,arguments);var d=this.context.data;jQuery(function(){jQuery.each(d,function(c,b){b.tooltip!==""&&a.tooltip.createTooltip(c,b.tooltip);b.autocomplete!==null&&a.autocomplete.makeAutoComplete(c,b.autocomplete)})})})();
