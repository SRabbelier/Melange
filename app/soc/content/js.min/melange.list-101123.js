(function(){function E(g,h,p,o){var b=this,y={datatype:F,viewrecords:true},t={edit:false,add:false,del:false,afterRefresh:function(){b.refreshData();b.jqgrid.object.trigger("reloadGrid")}};g=g;h=h;this.configuration=p;this.operations=o;this.jqgrid={id:null,object:null,options:null,last_selected_row:null,editable_columns:[],dirty_fields:{},pager:{id:null,options:null}};this.data={data:[],all_data:[],filtered_data:null};var v={enableDisableButtons:function(a){return function(d){function c(n){var i=
jQuery("#"+a.jqgrid.id).jqGrid("getRowData",n),f=s.from(a.data.all_data).equals("columns.key",i.key).select()[0];if(a.jqgrid.dirty_fields[i.key]===undefined)a.jqgrid.dirty_fields[i.key]=[];var j=[],u=[];jQuery.each(i,function(m,r){r!=f.columns[m]?j.push(m):u.push(m)});jQuery.each(j,function(m,r){jQuery.inArray(r,a.jqgrid.dirty_fields[i.key])===-1&&a.jqgrid.dirty_fields[i.key].push(r)});jQuery.each(u,function(m,r){m=jQuery.inArray(r,a.jqgrid.dirty_fields[i.key]);m!==-1&&a.jqgrid.dirty_fields[i.key].splice(m,
1)});a.jqgrid.dirty_fields[i.key].length===0&&delete a.jqgrid.dirty_fields[i.key];jQuery.each(a.operations.buttons,function(m,r){if(r.type==="post_edit"){m=jQuery("#"+a.jqgrid.id+"_buttonOp_"+r.id);D(a.jqgrid.dirty_fields)?m.attr("disabled","disabled"):m.removeAttr("disabled")}})}var k=a.jqgrid.object.jqGrid("getGridParam","multiselect")?"selarrrow":"selrow",e=a.jqgrid.object.jqGrid("getGridParam",k);if(!e instanceof Array)e=[e];if(e.length===1)if(d&&d!==a.jqgrid.last_selected_row){jQuery("#"+a.jqgrid.id).restoreRow(a.jqgrid.last_selected_row);
jQuery("#"+a.jqgrid.id).jqGrid("editRow",d,true,null,null,"clientArray",null,c);a.jqgrid.last_selected_row=d}jQuery.each(a.operations.buttons,function(n,i){n=jQuery("#"+a.jqgrid.id+"_buttonOp_"+i.id);if(i.type!=="post_edit")if(e.length>=i.real_bounds[0]&&e.length<=i.real_bounds[1]){n.removeAttr("disabled");if(i.real_bounds[0]===1&&i.real_bounds[1]===1&&n.data("melange")!==undefined){var f=a.jqgrid.object.jqGrid("getRowData",e[0]);f=s.from(a.data.all_data).equals("columns.key",f.key).select()[0];var j=
n.data("melange").click;n.click(j(f.operations.buttons[i.id].link));n.attr("value",f.operations.buttons[i.id].caption)}}else n.attr("disabled","disabled")})}}(b),global_button_functions:{redirect_simple:function(a){return a.new_window?function(){window.open(a.link)}:function(){window.location.href=a.link}},redirect_custom:function(a){return function(d){return a.new_window?function(){window.open(d)}:function(){window.location.href=d}}},post:function(a){return function(){var d=l.get(a.idx).jqgrid.object.jqGrid("getGridParam",
"multiselect")?"selarrrow":"selrow";d=l.get(a.idx).jqgrid.object.jqGrid("getGridParam",d);d instanceof Array||(d=d===null?[]:[d]);var c=[];if(!(d.length<a.real_bounds[0]||d.length>a.real_bounds[1])){jQuery.each(d,function(k,e){var n=jQuery("#"+l.get(a.idx).jqgrid.id).jqGrid("getRowData",e);s.from(l.get(a.idx).all_data).equals("columns.key",n.key).select();var i={};jQuery.each(a.keys,function(f,j){f=n[j];if(jQuery(f).parent().find("a.listsnoul").length)f=/^<a\b[^>]*>(.*?)<\/a>$/.exec(f)[1];i[j]=f});
c.push(i)});if(a.url==="")a.url=window.location.href;jQuery.post(a.url,{xsrf_token:window.xsrf_token,idx:a.idx,button_id:a.button_id,data:JSON.stringify(c)},function(k){if(a.redirect=="true")try{var e=JSON.parse(k);if(e.data.url!==undefined)window.location.href=e.data.url}catch(n){}k=parseInt(a.refresh,10);if(!isNaN(k)){l.get(k).refreshData();jQuery("#"+l.get(k).jqgrid.id).trigger("reloadGrid")}if(a.refresh=="current"){l.get(a.idx).refreshData();jQuery("#"+l.get(a.idx).jqgrid.id).trigger("reloadGrid")}else if(a.refresh==
"all"){k=l.getAll();jQuery.each(k,function(i,f){f.refreshData();jQuery("#"+l.get(i).jqgrid.id).trigger("reloadGrid")})}})}}},post_edit:function(a){return function(){var d=l.get(a.idx).jqgrid,c={};if(!(d.editable_columns.length===0&&D(d.dirty_fields))){for(var k=d.object.jqGrid("getGridParam","records"),e=1;e<=k;e++){var n=jQuery("#"+d.id).jqGrid("getRowData",e);if(d.dirty_fields[n.key]!==undefined){c[n.key]={};jQuery.each(d.dirty_fields[n.key],function(i,f){c[n.key][f]=n[f]})}}if(a.url==="")a.url=
window.location.href;jQuery.post(a.url,{xsrf_token:window.xsrf_token,idx:a.idx,button_id:a.button_id,data:JSON.stringify(c)},function(i){if(a.redirect=="true")try{var f=JSON.parse(i);if(f.data.url!==undefined)window.location.href=f.data.url}catch(j){}i=parseInt(a.refresh,10);if(!isNaN(i)){l.get(i).refreshData();jQuery("#"+l.get(i).jqgrid.id).trigger("reloadGrid")}if(a.refresh=="current"){l.get(a.idx).refreshData();jQuery("#"+l.get(a.idx).jqgrid.id).trigger("reloadGrid")}else if(a.refresh=="all"){i=
l.getAll();jQuery.each(i,function(u,m){m.refreshData();jQuery("#"+l.get(u).jqgrid.id).trigger("reloadGrid")})}})}}}},row_functions:{redirect_custom:function(a){return function(d,c){return a.new_window||c.which===2||c.which===1&&c.ctrlKey?function(){window.open(d)}:function(){window.location.href=d}}}}},C=function(){jQuery("#"+g).replaceWith(['<p id="temporary_list_placeholder_',h,'"></p>','<table id="'+b.jqgrid.id+'"',' cellpadding="0" cellspacing="0"></table>','<div id="'+b.jqgrid.pager.id+'"',' style="text-align:center"></div>'].join(""))},
z=function(){var a="",d=0,c=function(){var k="?";if(window.location.href.indexOf("?")!==-1)k="&";jQuery.ajax({async:true,cache:false,url:[window.location.href,k,"fmt=json&limit=150",a===""?"":"&start="+a,"&idx=",h].join(""),timeout:6E4,tryCount:1,retryLimit:5,error:function(e){if(e.status==500){this.tryCount++;if(this.tryCount<=this.retryLimit)jQuery.ajax(this);else{jQuery("#temporary_list_placeholder_"+h).html('<span style="color:red">Error retrieving data: please refresh the list or the whole page to try again</span>');
jQuery("#load_"+b.jqgrid.id).hide()}}else{jQuery("#temporary_list_placeholder_"+h).html('<span style="color:red">Error retrieving data: please refresh the list or the whole page to try again</span>');jQuery("#load_"+b.jqgrid.id).hide()}},success:function(e){e=JSON.parse(e);var n=d>0,i=!e.data[a].length;if(e.data[a]!==undefined&&(!n||!i)){if(b.configuration===null)b.configuration=e.configuration;if(b.operations===null)b.operations=e.operations;e=e.data[a];jQuery.each(e,function(){b.data.data.push(this.columns);
b.data.all_data.push(this)});b.jqgrid.object===null?w():b.jqgrid.object.trigger("reloadGrid");if(e[e.length-1]!==undefined){a=e[e.length-1].columns.key;setTimeout(c,100);d++}else{jQuery("#temporary_list_placeholder_"+h).remove();jQuery("#load_"+b.jqgrid.id).hide()}}else{jQuery("#temporary_list_placeholder_"+h).remove();jQuery("#load_"+b.jqgrid.id).hide();jQuery("#"+b.jqgrid.id)[0].triggerToolbar();jQuery.each(b.configuration.colModel,function(f,j){j.editable!==undefined&&j.editable===true&&b.jqgrid.editable_columns.push(j.name)});
jQuery("#t_"+b.jqgrid.id).children().remove();b.operations!==undefined&&b.operations.buttons!==undefined&&jQuery.each(b.operations.buttons,function(f,j){f=b.jqgrid.id+"_buttonOp_"+j.id;jQuery("#t_"+b.jqgrid.id).append("<input type='button' value='"+j.caption+"' style='float:left' id='"+f+"'/>");j.parameters.idx=h;if(j.type!=="post_edit"){j.real_bounds=j.bounds;var u=j.real_bounds.indexOf("all");if(u!==-1)j.real_bounds[u]=b.jqgrid.object.jqGrid("getGridParam","records");j.parameters.real_bounds=j.real_bounds}if(j.type===
"post_edit"||j.real_bounds[0]>0)jQuery("#"+f).attr("disabled","disabled");j.parameters.button_id=j.id;jQuery("#"+f).click(v.global_button_functions[j.type](j.parameters));j.type=="redirect_custom"&&jQuery("#"+f).data("melange",{click:v.global_button_functions[j.type](j.parameters)})});jQuery("#t_"+b.jqgrid.id).css("padding-bottom","3px");jQuery("#t_"+b.jqgrid.id).append("<input type='button' value='CSV Export' style='float:right' id='csvexport_"+b.jqgrid.id+"'/>");jQuery("#csvexport_"+b.jqgrid.id).click(function(){var f=
[];f[0]=[];if(b.data.data[0]!==undefined||b.data.filtered_data[0]!==undefined){var j=b.data.filtered_data||b.data.data;jQuery.each(b.configuration.colNames,function(m,r){m=r;m=m.replace(/\"|&quot;|&#34;/g,'""');if(m.indexOf(",")!==-1||m.indexOf('"')!==-1||m.indexOf("\r\n")!==-1)m='"'+m+'"';f[0].push(m)});f[0]=f[0].join(",");var u=[];jQuery.each(b.configuration.colModel,function(m,r){u.push(r.name)});jQuery.each(j,function(m,r){f[f.length]=[];jQuery.each(u,function(q,A){q=r[A];if(q===null)q="";if(q===
undefined)q="";q=q.toString();A=/^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(q);if(A!==null)q=A[1];q=q.replace(/\"|&quot;|&#34;/g,'""');if(q.indexOf(",")!==-1||q.indexOf('"')!==-1||q.indexOf("\r\n")!==-1)q='"'+q+'"';f[f.length-1].push(q)});f[f.length-1]=f[f.length-1].join(",")});f=f.join("\r\n");jQuery("#csv_thickbox").remove();jQuery("body").append("<div id='csv_thickbox' style='display:none'><h3>Now you can copy and paste CSV data from the text area to a new file:</h3><textarea style='width:450px;height:250px'>"+
f+"</textarea></div>");tb_show("CSV export","#TB_inline?height=400&width=500&inlineId=csv_thickbox")}});jQuery("#t_"+b.jqgrid.id).append("<div style='float:right;margin-right:4px;'><input type='checkbox' id='regexp_"+b.jqgrid.id+"'/>RegExp Search</div>");jQuery("#regexp_"+b.jqgrid.id).click(function(){jQuery("#"+b.jqgrid.id).jqGrid().trigger("reloadGrid")});e=jQuery.Event("melange_list_loaded");e.list_object=b;b.jqgrid.object.trigger(e)}}})};setTimeout(c,100)};this.refreshData=function(){b.data={data:[],
all_data:[],filtered_data:null};z()};var w=function(){var a=jQuery.extend(b.configuration,{postData:{my_index:h},onSelectAll:v.enableDisableButtons,onSelectRow:v.enableDisableButtons}),d={caption:"",buttonicon:"ui-icon-calculator",onClickButton:function(){jQuery("#"+b.jqgrid.id).setColumns({colnameview:false,jqModal:true,ShrinkToFit:true});return false},position:"last",title:"Show/Hide Columns",cursor:"pointer"};jQuery("#"+b.jqgrid.id).jqGrid(jQuery.extend(b.jqgrid.options,a)).jqGrid("navGrid","#"+
b.jqgrid.pager.id,b.jqgrid.pager.options,{},{},{},{closeAfterSearch:true,multipleSearch:true},{}).jqGrid("navButtonAdd","#"+b.jqgrid.pager.id,d);jQuery("#"+b.jqgrid.id).jqGrid("filterToolbar",{});jQuery("#load_"+b.jqgrid.id).closest("div").css("line-height","100%");jQuery("#load_"+b.jqgrid.id).html("<img src='/soc/content/images/jqgrid_loading.gif'></img>");jQuery("#load_"+b.jqgrid.id).show();b.jqgrid.object=jQuery("#"+b.jqgrid.id)};this.getDiv=function(){return g};this.getIdx=function(){return h};
(function(){jQuery(function(){if(jQuery("#"+g).length===0)throw new x.error.divNotExistent("Div "+g+" is not existent");b.jqgrid.id="jqgrid_"+g;b.jqgrid.pager.id="jqgrid_pager_"+g;b.jqgrid.options=jQuery.extend(y,{pager:"#"+b.jqgrid.pager.id});b.jqgrid.pager.options=t;l.add(b);C();w();z()})})()}if(window.melange===undefined)throw new Error("Melange not loaded");var x=window.melange;if(window.jLinq===undefined)throw new Error("jLinq not loaded");var s=window.jLinq;x.list=window.melange.list=function(){return new x.list};
var G=x.logging.debugDecorator(x.list);x.error.createErrors(["listIndexNotValid","divNotExistent","indexAlreadyExistent"]);var B=[];B[0]={configuration:{colNames:['yo"Key',"Link, ID","Name","Program Owner","Read"],colModel:[{name:"key",index:"key",resizable:true,hidden:true},{name:"link_id",index:"link_id",resizable:true,hidden:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true},{name:"read",index:"read",resizable:true,stype:"select",editoptions:{value:":All;^Read$:Posts Read;^Not Read$:Posts Unread"}}],
rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",height:"auto",multiselect:true,toolbar:[true,"top"]},operations:{buttons:[{bounds:[0,"all"],id:"bulk_process",caption:"Bulk Accept/Reject Organizations",type:"post",parameters:{url:""}},{bounds:[0,"all"],id:"add",caption:"Add a user",type:"redirect_simple",parameters:{link:"http://add1",new_window:true}},{bounds:[1,1],id:"edit",caption:"Edit user(s)",type:"redirect_custom",parameters:{new_window:true}},{bounds:[1,"all"],id:"delete",
caption:"Delete user(s)",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],refresh:"current"}},{bounds:[0,"all"],id:"dummy_0_all",caption:"Test 0-all range in POST",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],refresh:"current"}},{bounds:[0,"all"],id:"dummy_post_redirect",caption:"Test POST redirect",type:"post",parameters:{url:"/user/roles",keys:["key","link_id"],redirect:"true"}}],row:{type:"redirect_custom",parameters:{new_window:true}}},data:{"":[{columns:{key:"key_test",
link_id:"test",name:"Test Example",program_owner:"Google",read:"Read"},operations:{buttons:{edit:{caption:"Edit key_test user",link:"http://edit1"}},row:{link:"http://my_row_edit_link"}}},{columns:{key:"key_test2",link_id:"test2",name:"Test Example",program_owner:"GooglePlex",read:"Not Read"},operations:{edit:{caption:"Edit key_test2 user",link:"http://edit2"}}}],key_test2:[]}};B[1]={configuration:{colNames:["Key","Link ID","Name","Rank","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},
{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"rank",index:"rank",resizable:true,sorttype:"integer"},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[{columns:{key:"key_test3",link_id:"test3",name:"Mentor Test Example",rank:"10",program_owner:"melange"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}},{columns:{key:"key_test4",
link_id:"test4",name:"Mentor Test Example",rank:"12",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test4:[{columns:{key:"key_test5",link_id:"test5",name:"Mentor Test Example Loaded Incrementally",rank:"1",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test5:[{columns:{key:"key_test6",link_id:"test6",name:"Mentor Test Example Loaded Incrementally 2",rank:"2",program_owner:"google1"},
operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}]}};B[2]={configuration:{colNames:["Key","Link ID","Name","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[{columns:{key:"key_test7",link_id:"test7",name:"Admin Test Example",
program_owner:"melange"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}},{columns:{key:"key_test8",link_id:"test8",name:"Admin Test Example",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}],key_test8:[{columns:{key:"key_test9",link_id:"test9",name:"Admin Test Example Loaded Incrementally",program_owner:"google1"},operations:{edit:{caption:"Edit a user",link:"http://edit",new_window:true}}}]}};B[3]={configuration:{colNames:["Key",
"Link ID","Name","Program Owner"],colModel:[{name:"key",index:"key",resizable:true},{name:"link_id",index:"link_id",resizable:true},{name:"name",index:"name",resizable:true},{name:"program_owner",index:"program_owner",resizable:true}],rowNum:4,rowList:[4,8],autowidth:true,sortname:"link_id",sortorder:"asc",toolbar:[true,"top"]},data:{"":[]}};var D=function(g){for(var h in g)return false;return true},F=function(g){var h=g.my_index,p=l.get(h).data.data,o=p,b="",y={eq:{method:"equals",not:false},ne:{method:"equals",
not:true},lt:{method:"less",not:false},le:{method:"lessEquals",not:false},gt:{method:"greater",not:false},ge:{method:"greaterEquals",not:false},bw:{method:"startsWith",not:false},bn:{method:"startsWith",not:true},ew:{method:"endsWith",not:false},en:{method:"endsWith",not:true},cn:{method:"contains",not:false},nc:{method:"contains",not:true},"in":{method:"match",not:false},ni:{method:"match",not:true}};if(g._search&&g.filters){var t=JSON.parse(g.filters);if(t.rules[0].data!==""){b=t.groupOp;if(b===
"OR")o={};jQuery.each(t.rules,function(d,c){if(c.op==="in"||c.op==="ni")c.data=c.data.split(",").join("|");o=y[c.op].not?b==="OR"?s.from(o).union(s.from(p).not()[y[c.op].method](c.field,c.data).select()).select():s.from(o).not()[y[c.op].method](c.field,c.data).select():b==="OR"?s.from(o).union(s.from(p)[y[c.op].method](c.field,c.data).select()).select():s.from(o)[y[c.op].method](c.field,c.data).select()})}}else p[0]!==undefined&&jQuery.each(p[0],function(d){if(g[d]!==undefined){var c=jQuery("#regexp_"+
l.get(h).jqgrid.id).is(":checked"),k=false;jQuery.each(l.get(h).configuration.colModel,function(e,n){if(n.editoptions!==undefined&&d===n.name)k=true});o=c||k?s.from(o).match(d,g[d]).select():s.from(o).contains(d,g[d]).select()}});var v=g.sidx;t=g.sord;jQuery.each(l.get(h).configuration.colModel,function(d,c){if(c.name===v&&(c.sorttype==="integer"||c.sorttype==="int"))jQuery.each(o,function(k,e){k=parseInt(e[v],10);isNaN(k)||(e[v]=k)})});t=t==="asc"?"":"-";if(o.length>0)o=s.from(o).ignoreCase().orderBy(t+
v).select();l.get(h).data.filtered_data=o;if(g.rows===-1)g.rows=l.get(h).data.filtered_data.length;t=(g.page-1)*g.rows;for(var C=g.page*g.rows-1,z={page:g.page,total:o.length===0?0:Math.ceil(o.length/g.rows),records:o.length,rows:[]},w=t;w<=C;w++)if(o[w]!==undefined){var a=[];p[0]!==undefined&&jQuery.each(l.get(h).configuration.colModel,function(d,c){var k;d=l.get(h).data.all_data;for(var e=0;e<d.length;e++)if(d[e].columns.key===o[w].key){k=d[e];break}c=o[w][c.name];if(k.operations!==undefined&&k.operations.row!==
undefined&&k.operations.row.link!==undefined)if(c!==null&&c.toString().match(/<a\b[^>]*>.*<\/a>/)===null)c='<a style="display:block;" href="'+k.operations.row.link+'" class="listsnoul">'+c+"</a>";a.push(c)});z.rows.push({key:o[w].key,cell:a})}jQuery("#"+l.get(h).jqgrid.id)[0].addJSONData(z)},l=function(){var g=[];return{add:function(h){g[h.getIdx()]=h},get:function(h){return g[h]!==undefined?g[h]:null},getAll:function(){return jQuery.extend({},g)},isExistent:function(h){return g[h]!==undefined?true:
false}}}();G.loadList=function(g,h,p){p=parseInt(p,10);h=JSON.parse(h);if(isNaN(p)||p<0)throw new x.error.listIndexNotValid("List index "+p+" is not valid");if(l.isExistent(p))throw new x.error.indexAlreadyExistent("Index "+p+" is already existent");new E(g,p,h.configuration,h.operations)}})();