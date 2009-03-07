/**
 *  jquery.spin-button
 *  (c) 2008 Semooh (http://semooh.jp/)
 *
 *  Dual licensed under the MIT (MIT-LICENSE.txt)
 *  and GPL (GPL-LICENSE.txt) licenses.
 *
 **/
(function($){
  $.fn.extend({
    spin: function(opt){
      return this.each(function(){
        opt = $.extend({
            imageBasePath: '/soc/content/images/',
            spinBtnImage: 'spin-button.png',
            spinUpImage: 'spin-up.png',
            spinDownImage: 'spin-down.png',
            interval: 1,
            max: null,
            min: null,
            timeInterval: 500,
            timeBlink: 200
          }, opt || {});

        var txt = $(this);

        var spinBtnImage = opt.imageBasePath+opt.spinBtnImage;
        var btnSpin = new Image();
        btnSpin.src = spinBtnImage;
        var spinUpImage = opt.imageBasePath+opt.spinUpImage;
        var btnSpinUp = new Image();
        btnSpinUp.src = spinUpImage;
        var spinDownImage = opt.imageBasePath+opt.spinDownImage;
        var btnSpinDown = new Image();
        btnSpinDown.src = spinDownImage;

        var btn = $(document.createElement('img'));
        btn.attr('src', spinBtnImage);
        btn.css({cursor: 'pointer', verticalAlign: 'bottom', padding: 0, margin: 0});
        txt.after(btn);
        txt.css({marginRight:0, paddingRight:0});

        function spin(vector){
          var val = txt.val();
          if(!isNaN(val)){
            val = parseFloat(val) + (vector*opt.interval);
            if(opt.min!=null && val<opt.min) val=opt.min;
            if(opt.min!=null && val>opt.max) val=opt.max;
            if(val != txt.val()){
              txt.val(val);
              txt.change();
              src = (vector > 0 ? spinUpImage : spinDownImage);
              btn.attr('src', src);
              if(opt.timeBlink<opt.timeInterval)
                setTimeout(function(){btn.attr('src', spinBtnImage);}, opt.timeBlink);
            }
          }
        }

        btn.mousedown(function(e){
          var pos = e.pageY - btn.offset().top;
          var vector = (btn.height()/2 > pos ? 1 : -1);
          (function(){
            spin(vector);
            var tk = setTimeout(arguments.callee, opt.timeInterval);
            $(document).one('mouseup', function(){
              clearTimeout(tk); btn.attr('src', spinBtnImage);
            });
          })();
          return false;
        });
      });
    }
  });
})(jQuery);
