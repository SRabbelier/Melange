(function(b){b.jgrid.extend({setColumns:function(a){a=b.extend({top:0,left:0,width:200,height:"auto",dataheight:"auto",modal:false,drag:true,beforeShowForm:null,afterShowForm:null,afterSubmitForm:null,closeOnEscape:true,ShrinkToFit:false,jqModal:false,saveicon:[true,"left","ui-icon-disk"],closeicon:[true,"left","ui-icon-close"],onClose:null,colnameview:true,closeAfterSubmit:true,updateAfterCheck:false,recreateForm:false},b.jgrid.col,a||{});return this.each(function(){var c=this;if(c.grid){var j=typeof a.beforeShowForm===
"function"?true:false,k=typeof a.afterShowForm==="function"?true:false,l=typeof a.afterSubmitForm==="function"?true:false,e=c.p.id,d="ColTbl_"+e,f={themodal:"colmod"+e,modalhead:"colhd"+e,modalcontent:"colcnt"+e,scrollelm:d};a.recreateForm===true&&b("#"+f.themodal).html()!=null&&b("#"+f.themodal).remove();if(b("#"+f.themodal).html()!=null){j&&a.beforeShowForm(b("#"+d));viewModal("#"+f.themodal,{gbox:"#gbox_"+e,jqm:a.jqModal,jqM:false,modal:a.modal})}else{var g=isNaN(a.dataheight)?a.dataheight:a.dataheight+
"px";g="<div id='"+d+"' class='formdata' style='width:100%;overflow:auto;position:relative;height:"+g+";'>";g+="<table class='ColTable' cellspacing='1' cellpading='2' border='0'><tbody>";for(i=0;i<this.p.colNames.length;i++)c.p.colModel[i].hidedlg||(g+="<tr><td style='white-space: pre;'><input type='checkbox' style='margin-right:5px;' id='col_"+this.p.colModel[i].name+"' class='cbox' value='T' "+(this.p.colModel[i].hidden===false?"checked":"")+"/><label for='col_"+this.p.colModel[i].name+"'>"+this.p.colNames[i]+
(a.colnameview?" ("+this.p.colModel[i].name+")":"")+"</label></td></tr>");g+="</tbody></table></div>";g+="<table border='0' class='EditTable' id='"+d+"_2'><tbody><tr style='display:block;height:3px;'><td></td></tr><tr><td class='DataTD ui-widget-content'></td></tr><tr><td class='ColButton EditButton'>"+(!a.updateAfterCheck?"<a href='javascript:void(0)' id='dData' class='fm-button ui-state-default ui-corner-all'>"+a.bSubmit+"</a>":"")+"&#160;"+("<a href='javascript:void(0)' id='eData' class='fm-button ui-state-default ui-corner-all'>"+
a.bCancel+"</a>")+"</td></tr></tbody></table>";a.gbox="#gbox_"+e;createModal(f,g,a,"#gview_"+c.p.id,b("#gview_"+c.p.id)[0]);if(a.saveicon[0]==true)b("#dData","#"+d+"_2").addClass(a.saveicon[1]=="right"?"fm-button-icon-right":"fm-button-icon-left").append("<span class='ui-icon "+a.saveicon[2]+"'></span>");if(a.closeicon[0]==true)b("#eData","#"+d+"_2").addClass(a.closeicon[1]=="right"?"fm-button-icon-right":"fm-button-icon-left").append("<span class='ui-icon "+a.closeicon[2]+"'></span>");a.updateAfterCheck?
b(":input","#"+d).click(function(){var h=this.id.substr(4);if(h){this.checked?b(c).jqGrid("showCol",h):b(c).jqGrid("hideCol",h);a.ShrinkToFit===true&&b(c).jqGrid("setGridWidth",c.grid.width-0.0010,true)}return this}):b("#dData","#"+d+"_2").click(function(){for(i=0;i<c.p.colModel.length;i++)if(!c.p.colModel[i].hidedlg){var h=c.p.colModel[i].name.replace(".","\\.");if(b("#col_"+h,"#"+d).attr("checked")){b(c).jqGrid("showCol",c.p.colModel[i].name);b("#col_"+h,"#"+d).attr("defaultChecked",true)}else{b(c).jqGrid("hideCol",
c.p.colModel[i].name);b("#col_"+h,"#"+d).attr("defaultChecked","")}}a.ShrinkToFit===true&&b(c).jqGrid("setGridWidth",c.grid.width-0.0010,true);a.closeAfterSubmit&&hideModal("#"+f.themodal,{gb:"#gbox_"+e,jqm:a.jqModal,onClose:a.onClose});l&&a.afterSubmitForm(b("#"+d));return false});b("#eData","#"+d+"_2").click(function(){hideModal("#"+f.themodal,{gb:"#gbox_"+e,jqm:a.jqModal,onClose:a.onClose});return false});b("#dData, #eData","#"+d+"_2").hover(function(){b(this).addClass("ui-state-hover")},function(){b(this).removeClass("ui-state-hover")});
j&&a.beforeShowForm(b("#"+d));viewModal("#"+f.themodal,{gbox:"#gbox_"+e,jqm:a.jqModal,jqM:true,modal:a.modal})}k&&a.afterShowForm(b("#"+d))}})}})})(jQuery);