(function(){function D(f,e,s,j){var a=this,u={datatype:E,viewrecords:true},q={edit:false,add:false,del:false,afterRefresh:function(){a.refreshData();a.jqgrid.object.trigger("reloadGrid")}};f=f;e=e;this.configuration=s;this.operations=j;this.jqgrid={id:null,object:null,options:null,pager:{id:null,options:null}};this.data={data:[],all_data:[],filtered_data:null};var r={enableDisableButtons:function(b){return function(){var g=b.jqgrid.object.jqGrid("getGridParam","multiselect")?"selarrrow":"selrow",
c=b.jqgrid.object.jqGrid("getGridParam",g);if(!c instanceof Array)c=[c];jQuery.each(b.operations.buttons,function(k,d){k=jQuery("#"+b.jqgrid.id+"_buttonOp_"+d.id);if(c.length>=d.real_bounds[0]&&c.length<=d.real_bounds[1]){k.removeAttr("disabled");if(d.real_bounds[0]===1&&d.real_bounds[1]===1&&k.data("melange")!==undefined){var m=b.jqgrid.object.jqGrid("getRowData",c[0]);m=p.from(b.data.all_data).equals("columns.key",m.key).select()[0];var w=k.data("melange").click;k.click(w(m.operations.buttons[d.id].link));
k.attr("value",m.operations.buttons[d.id].caption)}}else k.attr("disabled","disabled")})}}(a),global_button_functions:{redirect_simple:function(b){return b.new_window?function(){window.open(b.link)}:function(){window.location.href=b.link}},redirect_custom:function(b){return function(g){return b.new_window?function(){window.open(g)}:function(){window.location.href=g}}},post:function(b){return function(){var g=l.get(b.idx).jqgrid.object.jqGrid("getGridParam","multiselect")?"selarrrow":"selrow";g=l.get(b.idx).jqgrid.object.jqGrid("getGridParam",
g);g instanceof Array||(g=g===null?[]:[g]);var c=[];if(!(g.length<b.real_bounds[0]||g.length>b.real_bounds[1])){jQuery.each(g,function(k,d){var m=jQuery("#"+l.get(b.idx).jqgrid.id).jqGrid("getRowData",d);p.from(l.get(b.idx).all_data).equals("columns.key",m.key).select();var w={};jQuery.each(b.keys,function(B,h){w[h]=m[h]});c.push(w)});if(b.url==="")b.url=window.location.href;jQuery.post(b.url,{xsrf_token:window.xsrf_token,idx:b.idx,button_id:b.button_id,data:JSON.stringify(c)},function(k){if(b.redirect==
"true")try{var d=JSON.parse(k);if(d.data.url!==undefined)window.location.href=d.data.url}catch(m){}if(b.refresh=="table"){l.get(b.idx).refreshData();jQuery("#"+l.get(b.idx).jqgrid.id).trigger("reloadGrid")}})}}}},row_functions:{redirect_custom:function(b){return function(g,c){return b.new_window||c.which===2||c.which===1&&c.ctrlKey?function(){window.open(g)}:function(){window.location.href=g}}}}},C=function(){jQuery("#"+f).replaceWith(['<p id="temporary_list_placeholder_',e,'">Please wait while list is loading</p>',
'<table id="'+a.jqgrid.id+'"',' cellpadding="0" cellspacing="0"></table>','<div id="'+a.jqgrid.pager.id+'"',' style="text-align:center"></div>'].join(""))},z=function(){var b="",g=0,c=function(){var k="?";if(window.location.href.indexOf("?")!==-1)k="&";jQuery.ajax({async:true,cache:false,url:[window.location.href,k,"fmt=json&limit=150",b===""?"":"&start="+b,"&idx=",e].join(""),timeout:6E4,tryCount:1,retryLimit:5,error:function(d){if(d.status==500){this.tryCount++;if(this.tryCount<=this.retryLimit)jQuery.ajax(this);
else{jQuery("#temporary_list_placeholder_"+e).html('<span style="color:red">Error retrieving data: please refresh the list or the whole page to try again</span>');jQuery("#load_"+a.jqgrid.id).hide()}}else{jQuery("#temporary_list_placeholder_"+e).html('<span style="color:red">Error retrieving data: please refresh the list or the whole page to try again</span>');jQuery("#load_"+a.jqgrid.id).hide()}},success:function(d){d=JSON.parse(d);var m=g>0,w=!d.data[b].length;if(d.data[b]!==undefined&&(!m||!w)){if(a.configuration===
null)a.configuration=d.configuration;if(a.operations===null)a.operations=d.operations;d=d.data[b];jQuery.each(d,function(){a.data.data.push(this.columns);a.data.all_data.push(this)});a.jqgrid.object===null?v():a.jqgrid.object.trigger("reloadGrid");if(d[d.length-1]!==undefined){b=d[d.length-1].columns.key;setTimeout(c,100);g++}else{jQuery("#temporary_list_placeholder_"+e).remove();jQuery("#load_"+a.jqgrid.id).hide()}}else{jQuery("#temporary_list_placeholder_"+e).remove();jQuery("#load_"+a.jqgrid.id).hide();
jQuery("#t_"+a.jqgrid.id).children().remove();a.operations!==undefined&&a.operations.buttons!==undefined&&jQuery.each(a.operations.buttons,function(h,i){h=a.jqgrid.id+"_buttonOp_"+i.id;jQuery("#t_"+a.jqgrid.id).append("<input type='button' value='"+i.caption+"' style='float:left' id='"+h+"'/>");i.parameters.idx=e;i.real_bounds=i.bounds;var x=i.real_bounds.indexOf("all");if(x!==-1)i.real_bounds[x]=a.jqgrid.object.jqGrid("getGridParam","records");i.real_bounds[0]>0&&jQuery("#"+h).attr("disabled","disabled");
i.parameters.real_bounds=i.real_bounds;i.parameters.button_id=i.id;jQuery("#"+h).click(r.global_button_functions[i.type](i.parameters));i.type=="redirect_custom"&&jQuery("#"+h).data("melange",{click:r.global_button_functions[i.type](i.parameters)})});var B=a.jqgrid.object.jqGrid("getGridParam","multiselect");if(a.operations!==undefined&&a.operations.row!==undefined&&!F(a.operations.row)){jQuery("body").live("mouseover",function(){B?jQuery("#"+a.jqgrid.id+" tbody tr td:gt(0)").css("cursor","pointer"):
jQuery("#"+a.jqgrid.id+" tbody tr td").css("cursor","pointer")});d=a.operations.row;d.parameters.idx=e;d.type=="redirect_custom"&&a.jqgrid.object.data("melange",{rowsel:r.row_functions[d.type](d.parameters)});a.jqgrid.object.jqGrid("setGridParam",{onCellSelect:function(h,i,x,n){if(!(B&&i==0)){h=jQuery("#"+a.jqgrid.id).jqGrid("getRowData",h);h=p.from(a.data.all_data).equals("columns.key",h.key).select()[0];i=a.jqgrid.object.data("melange").rowsel;i(h.operations.row.link,n)()}}})}jQuery("#t_"+a.jqgrid.id).css("padding-bottom",
"3px");jQuery("#t_"+a.jqgrid.id).append("<input type='button' value='CSV Export' style='float:right' id='csvexport_"+a.jqgrid.id+"'/>");jQuery("#csvexport_"+a.jqgrid.id).click(function(){var h=[];h[0]=[];if(a.data.data[0]!==undefined||a.data.filtered_data[0]!==undefined){var i=a.data.filtered_data||a.data.data;jQuery.each(a.configuration.colNames,function(n,y){n=y;n=n.replace(/\"|&quot;|&#34;/g,'""');if(n.indexOf(",")!==-1||n.indexOf('"')!==-1||n.indexOf("\r\n")!==-1)n='"'+n+'"';h[0].push(n)});h[0]=
h[0].join(",");var x=[];jQuery.each(a.configuration.colModel,function(n,y){x.push(y.name)});jQuery.each(i,function(n,y){h[h.length]=[];jQuery.each(x,function(o,G){o=y[G];if(o===null)o="";o=o.toString();o=o.replace(/\"|&quot;|&#34;/g,'""');if(o.indexOf(",")!==-1||o.indexOf('"')!==-1||o.indexOf("\r\n")!==-1)o='"'+o+'"';h[h.length-1].push(o)});h[h.length-1]=h[h.length-1].join(",")});h=h.join("\r\n");jQuery("#csv_thickbox").remove();jQuery("body").append("<div id='csv_thickbox' style='display:none'><h3>Now you can copy and paste CSV data from the text area to a new file:</h3><textarea style='width:450px;height:250px'>"+
h+"</textarea></div>");tb_show("CSV export","#TB_inline?height=400&width=500&inlineId=csv_thickbox")}});jQuery("#t_"+a.jqgrid.id).append("<div style='float:right;margin-right:4px;'><input type='checkbox' id='regexp_"+a.jqgrid.id+"'/>RegExp Search</div>");jQuery("#regexp_"+a.jqgrid.id).click(function(){jQuery("#"+a.jqgrid.id).jqGrid().trigger("reloadGrid")});d=jQuery.Event("melange_list_loaded");d.list_object=a;a.jqgrid.object.trigger(d)}}})};setTimeout(c,100)};this.refreshData=function(){a.data={data:[],
all_data:[],filtered_data:null};z()};var v=function(){var b=jQuery.extend(a.configuration,{postData:{my_index:e},onSelectAll:r.enableDisableButtons,onSelectRow:r.enableDisableButtons}),g={caption:"",buttonicon:"ui-icon-calculator",onClickButton:function(){jQuery("#"+a.jqgrid.id).setColumns({colnameview:false,jqModal:true,ShrinkToFit:true});return false},position:"last",title:"Show/Hide Columns",cursor:"pointer"};jQuery("#"+a.jqgrid.id).jqGrid(jQuery.extend(a.jqgrid.options,b)).jqGrid("navGrid","#"+
a.jqgrid.pager.id,a.jqgrid.pager.options,{},{},{},{closeAfterSearch:true,multipleSearch:true},{}).jqGrid("navButtonAdd","#"+a.jqgrid.pager.id,g);jQuery("#"+a.jqgrid.id).jqGrid("filterToolbar",{});jQuery("#load_"+a.jqgrid.id).closest("div").css("line-height","100%");jQuery("#load_"+a.jqgrid.id).html("<img src='/soc/content/images/jqgrid_loading.gif'></img>");jQuery("#load_"+a.jqgrid.id).show();a.jqgrid.object=jQuery("#"+a.jqgrid.id)};(function(){jQuery(function(){if(jQuery("#"+f).length===0)throw new t.error.divNotExistent("Div "+
f+" is not existent");a.jqgrid.id="jqgrid_"+f;a.jqgrid.pager.id="jqgrid_pager_"+f;a.jqgrid.options=jQuery.extend(u,{pager:"#"+a.jqgrid.pager.id});a.jqgrid.pager.options=q;C();z()})})();this.getDiv=function(){return f};this.getIdx=function(){return e}}if(window.melange===undefined)throw new Error("Melange not loaded");var t=window.melange;if(window.jLinq===undefined)throw new Error("jLinq not loaded");var p=window.jLinq;t.list=window.melange.list=function(){return new t.list};var H=t.logging.debugDecorator(t.list);
t.error.createErrors(["listIndexNotValid","divNotExistent","indexAlreadyExistent"]);var A=[];A[0]={configuration:{colNames:['yo"Key',"Link, ID","Name","Program Owner","Read"],colModel:[{name:"key",index:"key",resizable:true,hidden:true},{name:"link_id",index:"link_id",resizable:true,hidden:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true},{name:"read",index:"read",resizable:true,stype:"select",editoptions:{value:":All;^Read$:Posts Read;^Not Read$:Posts Unread"}}],
rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",height:"auto",multiselect:true,toolbar:[true,"top"]},operations:{buttons:[{bounds:[0,"all"],id:"bulk_process",caption:"Bulk Accept/Reject Organizations",type:"post",parameters:{url:""}},{bounds:[0,"all"],id:"add",caption:"Add a user",type:"redirect_simple",parameters:{link:"http://add1",new_window:true}},{bounds:[1,1],id:"edit",caption:"Edit user(s)",type:"redirect_custom",parameters:{new_window:true}},{bounds:[1,"all"],id:"delete",
caption:"Delete user(s)",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],refresh:"table"}},{bounds:[0,"all"],id:"dummy_0_all",caption:"Test 0-all range in POST",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],refresh:"table"}},{bounds:[0,"all"],id:"dummy_post_redirect",caption:"Test POST redirect",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],redirect:"true"}}],row:{type:"redirect_custom",parameters:{new_window:true}}},data:{"":[{columns:{key:"key_test",
link_id:"test",name:"Test Example",program_owner:"Google",read:"Read"},operations:{buttons:{edit:{caption:"Edit key_test user",link:"http://edit1"}},row:{link:"http://my_row_edit_link"}}},{columns:{key:"key_test2",link_id:"test2",name:"Test Example",program_owner:"GooglePlex",read:"Not Read"},operations:{edit:{caption:"Edit key_test2 user",link:"http://edit2"}}}],key_test2:[]}};A[1]={configuration:{colNames:["Key","Link ID","Name","Rank","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},
{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"rank",index:"rank",resizable:true,sorttype:"integer"},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[{columns:{key:"key_test3",link_id:"test3",name:"Mentor Test Example",rank:"10",program_owner:"melange"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}},{columns:{key:"key_test4",
link_id:"test4",name:"Mentor Test Example",rank:"12",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test4:[{columns:{key:"key_test5",link_id:"test5",name:"Mentor Test Example Loaded Incrementally",rank:"1",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test5:[{columns:{key:"key_test6",link_id:"test6",name:"Mentor Test Example Loaded Incrementally 2",rank:"2",program_owner:"google1"},
operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}]}};A[2]={configuration:{colNames:["Key","Link ID","Name","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[{columns:{key:"key_test7",link_id:"test7",name:"Admin Test Example",
program_owner:"melange"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}},{columns:{key:"key_test8",link_id:"test8",name:"Admin Test Example",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test8:[{columns:{key:"key_test9",link_id:"test9",name:"Admin Test Example Loaded Incrementally",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}]}};A[3]={configuration:{colNames:["Key",
"Link ID","Name","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[]}};var F=function(f){for(var e in f)return false;return true},E=function(f){var e=f.my_index,s=l.get(e).data.data,j=s,a="",u={eq:{method:"equals",not:false},ne:{method:"equals",
not:true},lt:{method:"less",not:false},le:{method:"lessEquals",not:false},gt:{method:"greater",not:false},ge:{method:"greaterEquals",not:false},bw:{method:"startsWith",not:false},bn:{method:"startsWith",not:true},ew:{method:"endsWith",not:false},en:{method:"endsWith",not:true},cn:{method:"contains",not:false},nc:{method:"contains",not:true},"in":{method:"match",not:false},ni:{method:"match",not:true}};if(f._search&&f.filters){var q=JSON.parse(f.filters);if(q.rules[0].data!==""){a=q.groupOp;if(a===
"OR")j={};jQuery.each(q.rules,function(g,c){if(c.op==="in"||c.op==="ni")c.data=c.data.split(",").join("|");j=u[c.op].not?a==="OR"?p.from(j).union(p.from(s).not()[u[c.op].method](c.field,c.data).select()).select():p.from(j).not()[u[c.op].method](c.field,c.data).select():a==="OR"?p.from(j).union(p.from(s)[u[c.op].method](c.field,c.data).select()).select():p.from(j)[u[c.op].method](c.field,c.data).select()})}}else s[0]!==undefined&&jQuery.each(s[0],function(g){if(f[g]!==undefined){var c=jQuery("#regexp_"+
l.get(e).jqgrid.id).is(":checked"),k=false;jQuery.each(l.get(e).configuration.colModel,function(d,m){if(m.editoptions!==undefined&&g===m.name)k=true});j=c||k?p.from(j).match(g,f[g]).select():p.from(j).contains(g,f[g]).select()}});var r=f.sidx;q=f.sord;jQuery.each(l.get(e).configuration.colModel,function(g,c){if(c.name===r&&(c.sorttype==="integer"||c.sorttype==="int"))jQuery.each(j,function(k,d){k=parseInt(d[r],10);isNaN(k)||(d[r]=k)})});q=q==="asc"?"":"-";if(j.length>0)j=p.from(j).orderBy(q+r).select();
l.get(e).data.filtered_data=j;if(f.rows===-1)f.rows=l.get(e).data.filtered_data.length;q=(f.page-1)*f.rows;for(var C=f.page*f.rows-1,z={page:f.page,total:j.length===0?0:Math.ceil(j.length/f.rows),records:j.length,rows:[]},v=q;v<=C;v++)if(j[v]!==undefined){var b=[];s[0]!==undefined&&jQuery.each(l.get(e).configuration.colModel,function(g,c){b.push(j[v][c.name])});z.rows.push({key:j[v].key,cell:b})}jQuery("#"+l.get(e).jqgrid.id)[0].addJSONData(z)},l=function(){var f=[];return{add:function(e){f[e.getIdx()]=
e},get:function(e){return f[e]!==undefined?f[e]:null},getAll:function(){return jQuery.extend({},f)},isExistent:function(e){return f[e]!==undefined?true:false}}}();H.loadList=function(f,e){e=parseInt(e,10);if(isNaN(e)||e<0)throw new t.error.listIndexNotValid("List index "+e+" is not valid");if(l.isExistent(e))throw new t.error.indexAlreadyExistent("Index "+e+" is already existent");f=new D(f,e,null,null);l.add(f)}})();