(function(b){b.fn.inPlaceEdit=function(e){return this.each(function(){function g(){a.html(a.old_value);a.removeClass("hover editing");e.cancel&&e.cancel.apply(a,[a]);return false}function h(){clearTimeout(a.timeout);var c=a.attr("id"),f=b(".field",a).val();e.submit&&e.submit.apply(a,[a,c,f,a.old_value]);a.removeClass("hover editing");a.html(f);return false}var d=b.extend({},b.fn.inPlaceEdit.defaults,e),a=b(this);a.click(function(){a.data("skipBlur",false);if(!(a.hasClass("editing")||a.hasClass("disabled"))){a.addClass("editing");
a.old_value=a.html();if(typeof d.html=="string")a.html(d.html);else{a.html("");d.html.children(":first").clone(true).appendTo(a)}b(".field",a).val(a.old_value);b(".field",a).focus();b(".field",a).select();d.onBlurDisabled==false&&b(".field",a).blur(function(){if(a.data("skipBlur")!=true)a.timeout=setTimeout(g,50);a.data("skipBlur",false)});b(".save-button",a).click(function(){return h()});b(".save-button",a).mousedown(function(){a.data("skipBlur",true)});b(".cancel-button",a).mousedown(function(){a.data("skipBlur",
true)});b(".cancel-button",a).click(function(){return g()});d.onKeyupDisabled==false&&b(".field",a).keyup(function(c){c=c.which;var f=this.tagName.toLowerCase();if(c==27&&d.escapeKeyDisabled==false)return g();else if(c==13)if(f!="textarea")return h();return true})}});a.mouseover(function(){a.addClass("hover")});a.mouseout(function(){a.removeClass("hover")})})};b.fn.inPlaceEdit.defaults={onBlurDisabled:false,onKeyupDisabled:false,escapeKeyDisabled:false,html:'           <div class="inplace-edit">             <input type="text" value="" class="field" />             <div class="buttons">               <input type="button" value="Save" class="save-button" />               <input type="button" value="Cancel" class="cancel-button" />             </div>           </div>'}})(jQuery);
