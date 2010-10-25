var jLinq;
(function(){var Q=function(a){var b=this,c={};c.settings=a;b.finish=function(d){b.finish=null;c.loaded=true;c.lock=d};c.util={format:function(d,h){return d.toString().replace(/%[0-9]+%/gi,function(e){e=parseInt(e.replace(/%/gi,""));return h[e]})},allValues:function(d){for(var h=[],e=0;e<d.length;e++){if(d[e]==null)return h;h.push(d[e])}return h},trim:function(d){if(d==null)return"";return d.toString().replace(/^\s+|\s+$/,"")},empty:function(d){for(var h=0;h<d.length;h++)if(d[h])return false;return true},
type:function(d){if(d==null)return"null";if(d==undefined)return"null";for(var h in c.types)try{if(c.types[h](d))return h}catch(e){}return(typeof d).toString().toLowerCase()},when:function(d,h){var e=c.util.type(d);if(!h[e]){if(h.empty&&(d==null||d==undefined))return h.empty(d);if(h.other)return h.other(d);return false}try{return h[e](d)}catch(p){return false}},as:function(d,h){var e=c.util.type(d);if(!h[e]){if(h.empty&&(d==null||d==undefined))return h.empty(d);if(h.other)return h.other(d);return null}try{return h[e](d)}catch(p){return null}},
each:function(d,h){for(var e=[],p=0;p<d.length;p++)try{e.push(h(d[p],p))}catch(f){e.push(f)}return e},clone:function(d){function h(){}h.prototype=d;return new h}};b.addType=function(d,h){d=c.util.trim(d).toLowerCase();c.types[d]=h};b.removeType=function(d){d=c.util.trim(d).toLowerCase();c.types[d]=function(){return false}};c.types=a.types?a.types:{};b.extend=function(d){d.name=c.util.trim(d.name);d.namespace=c.util.trim(d.namespace);if(c.extend.hasCmd(d)){if(c.lock)throw"Exception: Library is locked.";
c.extend.removeCmd(d)}c.extend.addCmd(d);if(d.type.match(/source/i)){if(d.namespace&&!b[d.namespace])b[d.namespace]={};(d.namespace==""?b:b[d.namespace])[d.name]=function(h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E){h=d.method({helper:c.util},h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E);if(c.util.type(h)!="array")throw"Exception: A 'Source' extension must return an array for a jLinq query.";return new c.query(h)}}};c.extend={cmd:[],hasCmd:function(d){return c.extend.findCmd(d)!=null},
addCmd:function(d){c.extend.removeCmd(d);c.extend.cmd.push(d)},removeCmd:function(d){(d=c.extend.findCmd(d))&&c.extend.cmd.splice(d,1)},findCmd:function(d){for(var h=0;h<c.extend.cmd.length;h++){var e=c.extend.cmd[h];if(e.name==d.name&&e.namespace==d.namespace)return h}return null}};b.showCommands=function(){return c.util.clone(c.extend.cmd)};for(var g in a.extend)b.extend(a.extend[g]);c.query=function(d){var h=this;d=c.util.clone(d);var e={};e.state={properties:true,lastCommand:null,lastField:null,
lastCommandName:null,paramCount:0,ignoreCase:true,or:false,not:false,data:d,useProperties:false,operator:"",debug:{onEvent:function(){},log:function(f,j){e.state.debug.onEvent(c.util.format(f,j))}}};if(d==null)return null;if(c.util.type(d)=="array"&&d.length>0)e.state.useProperties=c.util.type(d[0])=="object";e.query={cache:[],str:[],appendCmd:function(f){e.query.cache.push(f);f=e.state.not?"!":"";if(e.query.cache.length==0)e.state.operator="";e.state.or=false;e.state.not=false;e.query.str.push([e.state.operator,
"(",f,"(_s.query.cache[",e.query.cache.length-1,"](record)))"].join(""));e.state.operator="&&"},select:function(){if(e.query.str.length==0)return{selected:e.state.data,remaining:[]};var f;eval(["query = function(record) { return (",e.query.str.join(""),"); };"].join(""));for(var j=[],i=[],l=0;l<e.state.data.length;l++){var k=e.state.data[l];try{f(k)?j.push(k):i.push(k)}catch(m){e.state.debug.log("Exception when evaluating the query for selection: %0%. query: %1%",[m,f]);i.push(k)}}return{selected:j,
remaining:i}},prepCmd:function(f,j){e.state.lastCommand=f.command;e.state.paramCount=f.count;e.state.lastCommandName=f.name;for(var i=[],l=false,k=j.length;k-- >0;)if(j[k]||l){l=true;i.push(j[k])}i.reverse();if(e.state.useProperties&&i.length==f.count+1)e.state.lastField=i.shift();return{arg:i,field:e.state.lastField}},repeatCmd:function(f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H){e.helper.empty([f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H])||e.state.lastCommand(f,j,i,l,k,m,n,o,r,q,s,
t,u,v,w,x,y,z,B,C,D,E,F,G,H)},performSort:function(f,j,i){f.sort(function(l,k){l=l[j];k=k[j];if(e.state.ignoreCase&&e.helper.type(l)=="string"&&e.helper.type(k)=="string"){l=l.toLowerCase();k=k.toLowerCase()}return l<k?-1:l>k?1:0});i&&f.reverse()}};e.helper={toRegex:function(f){if(f==null)return"";return f.toString().replace(/\*|\(|\)|\\|\/|\?|\.|\*|\+|\<|\>|\[|\]|\=|\&|\$|\^/gi,function(j){return"\\"+j})},getNumericValue:function(f){if(f.length)return f.length;return f},trim:c.util.trim,match:function(f,
j){if(!(f&&j))return false;if(e.helper.type(j)=="regexp")j=j.source;j=new RegExp(j,"g"+(e.state.ignoreCase?"i":""));return f.match(j)},propsEqual:function(f,j){if(f==null&&j==null)return true;if(f==null||j==null)return false;for(var i in f){if(j[i]==undefined)return false;if(!e.helper.equals(f[i],j[i]))return false}return true},equals:function(f,j){try{if(f==null&&j==null)return true;if(f==null&&j||f&&j==null)return false;var i=e.helper.type(f),l=e.helper.type(j);if(i!=l)return false;if(i=="string"&&
l=="string")return e.helper.match(f,"^"+j+"$");if(i=="string"&&l=="regexp")return e.helper.match(f,j);if(i=="number"||i=="bool")return f==j;else if(i=="array"||i=="object"){if(f.length!=j.length)return false;for(i=0;i<f.length;i++)if(!e.helper.equals(f[i],j[i]))return false;return true}else return f==j}catch(k){return false}},allEqual:function(f,j){if(c.helper.type(f)!="array")f=[f];for(var i in f)if(!c.helper.equals(f[i],j))return false;return true},anyEqual:function(f,j){if(c.helper.type(f)!="array")f=
[f];for(var i in f)if(!c.helper.equals(f[i],j))return true;return false},sort:function(f,j,i){if(j==null){f.sort();i&&query.state.data.reverse();return f}var l=0,k=function(m){m=c.util.clone(m);var n=j[l].field,o=j[l].desc;if(l==j.length-1){e.query.performSort(m,n,o);return m}e.query.performSort(m,n,o);m=e.helper.distinct(m,n);l++;n=[];for(o=0;o<m.length;o++)for(var r=k(m[o].items),q=0;q<r.length;q++)n.push(r[q]);return n};return k(e.state.data)},distinct:function(f,j){for(var i=[],l=0;l<f.length;l++){var k=
f[l],m=j!=null?eval(["(val.",j,")"].join("")):k,n=false;for(var o in i)if(i[o].key===m){n=true;i[o].items.push(k);break}n||i.push({key:m,items:[k]})}return i},empty:c.util.empty,type:c.util.type,when:c.util.when,each:c.util.each,format:c.util.format,clone:c.util.clone,all:c.util.allValues,as:c.util.as};for(var p in c.extend.cmd)(function(f){if(f.type||f.name||f.method)if(!f.type.match(/source/i)){if(f.namespace&&!h[f.namespace])h[f.namespace]={};var j=f.namespace?h[f.namespace]:h,i=function(k,m,n,
o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.debug.log("Called command %0% '%1%()'.",[f.type,f.name]);var M={add:function(N){e.query.str.push(N)},query:h,state:e.state,helper:e.helper,repeat:function(N,O,P,S,T,U,V,W,X,Y,Z,$,aa,ba,ca,da,ea,fa,ga,ha,ia,ja,ka,la,ma){e.query.repeatCmd(N,O,P,S,T,U,V,W,X,Y,Z,$,aa,ba,ca,da,ea,fa,ga,ha,ia,ja,ka,la,ma)}};if(f.type.match(/^query$/i)){var A=e.query.prepCmd({command:j[f.name],count:f.count,name:f.name},[k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,
L]);e.query.appendCmd(function(N){try{M.value=e.state.useProperties?eval("record."+A.field):N}catch(O){e.state.debug.log("Exception when calling '%0%()' : %1%.",[f.name,O]);M.value=null}M.record=N;M.type=M.helper.type(M.value);M.when=function(P){return e.helper.when(M.value,P)};return f.method(M,A.arg[0],A.arg[1],A.arg[2],A.arg[3],A.arg[4],A.arg[5],A.arg[6],A.arg[7],A.arg[8],A.arg[9],A.arg[10],A.arg[11],A.arg[12],A.arg[13],A.arg[14],A.arg[15],A.arg[16],A.arg[17],A.arg[18],A.arg[19],A.arg[20],A.arg[21],
A.arg[22],A.arg[23],A.arg[24])});return h}else if(f.type.match(/^action$/i)){try{f.method(M,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)}catch(na){e.state.debug.log("Exception when calling '%0%()' : %1%.",[f.name,na])}return h}else if(f.type.match(/^selection$/i)){M.results=f.manual?[]:e.query.select();M.select=e.query.select;return f.method(M,k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)}return h};j[f.name]=i;if(f.type.match(/^query$/i)&&(c.settings.generate==null||c.settings.generate)&&
(f.generate==null||f.generate)){var l=f.name.substr(0,1).toUpperCase()+f.name.substr(1,f.name.length-1);j["or"+l]=function(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.operator="||";return i(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)};j["and"+l]=function(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.operator="&&";return i(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)};j["not"+l]=function(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.not=!e.state.not;
return i(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)};j["andNot"+l]=function(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.not=!e.state.not;e.state.operator="&&";return i(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)};j["orNot"+l]=function(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L){e.state.not=!e.state.not;e.state.operator="||";return i(k,m,n,o,r,q,s,t,u,v,w,x,y,z,B,C,D,E,F,G,H,I,J,K,L)}}}})(c.extend.cmd[p])}},R=function(){return{locked:true,generate:true,types:{array:function(a){return a.push&&
a.pop&&a.reverse&&a.slice&&a.splice},"function":function(a){return(typeof a).toString().match(/^function$/i)},string:function(a){return(typeof a).toString().match(/^string$/i)},number:function(a){return(typeof a).toString().match(/^number$/i)},bool:function(a){return(typeof a).toString().match(/^boolean$/i)},regexp:function(a){return a.ignoreCase!=null&&a.global!=null&&a.exec},date:function(a){return a.getTime&&a.setTime&&a.toDateString&&a.toTimeString}},extend:[{name:"from",type:"source",method:function(a,
b){return a.helper.when(b,{"function":function(){return b()},array:function(){return b},other:function(){return[b]}})}},{name:"debug",type:"action",operators:false,method:function(a,b){a.state.debug.onEvent=b}},{name:"reverse",type:"action",method:function(a){a.state.data.reverse()}},{name:"ignoreCase",type:"action",method:function(a){a.state.ignoreCase=true}},{name:"useCase",type:"action",method:function(a){a.state.ignoreCase=false}},{name:"or",type:"action",method:function(a,b,c,g,d,h,e,p,f,j,i,
l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){a.state.operator="||";a.repeat(b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z)}},{name:"not",type:"action",method:function(a,b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){a.state.not=!a.state.not;a.repeat(b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z)}},{name:"and",type:"action",method:function(a,b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){a.state.operator="&&";a.repeat(b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z)}},{name:"orNot",type:"action",
method:function(a,b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){a.state.or=true;a.state.not=!a.state.not;a.repeat(b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z)}},{name:"andNot",type:"action",method:function(a,b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){a.state.or=false;a.state.not=!a.state.not;a.repeat(b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z)}},{name:"combine",type:"action",method:function(a,b){a.add(a.state.operator+"("+(a.state.not?"!":""));a.state.operator="";b(a.query);
a.add(")")}},{name:"orCombine",type:"action",method:function(a,b){a.state.operator="||";a.add(a.state.operator+"("+(a.state.not?"!":""));a.state.operator="";b(a.query);a.add(")")}},{name:"where",count:-1,type:"query",method:function(a,b){return b(a.record,a.helper)}},{name:"has",count:1,type:"query",method:function(a,b){b=parseInt(b.toString(),16);return(parseInt(a.value.toString(),16)&b)==b}},{name:"equals",count:1,type:"query",method:function(a,b){return a.helper.equals(a.value,b)}},{name:"startsWith",
count:1,type:"query",method:function(a,b){if(a.helper.type(b)!="array")b=[b];for(var c in b){var g=b[c];if(a.when({array:function(){return a.helper.equals(a.value[0],g)},other:function(){return a.helper.match(a.value.toString(),"^"+g.toString())}}))return true}}},{name:"endsWith",count:1,type:"query",method:function(a,b){if(a.helper.type(b)!="array")b=[b];for(var c in b){var g=b[c];if(a.when({array:function(){return a.helper.equals(a.value[a.value.length-1],g)},other:function(){return a.helper.match(a.value.toString(),
g.toString()+"$")}}))return true}}},{name:"contains",count:1,type:"query",method:function(a,b){if(b==null)return false;if(a.helper.type(b)!="array")b=[b];for(var c in b){var g=b[c];if(a.when({array:function(){for(var d=0;d<a.value.length;d++)if(a.helper.equals(a.value[d],g))return true},other:function(){return a.helper.match(a.value.toString(),"^.*"+a.helper.toRegex(g)+".*$")}}))return true}}},{name:"match",count:1,type:"query",method:function(a,b){if(a.helper.type(b)!="array")b=[b];for(var c in b){var g=
b[c];if(a.when({array:function(){for(var d=0;d<a.value.length;d++)if(a.helper.match(a.value[d],g))return true},other:function(){return a.helper.match(a.value.toString(),g)}}))return true}}},{name:"less",count:1,type:"query",method:function(a,b){b=a.helper.when(b,{number:function(){return b},date:function(){return b},other:function(){return b.length}});return a.when({string:function(){return a.value.length<b},array:function(){return a.value.length<b},other:function(){return a.value<b}})}},{name:"greater",
count:1,type:"query",method:function(a,b){b=a.helper.when(b,{number:function(){return b},date:function(){return b},other:function(){return b.length}});return a.when({string:function(){return a.value.length>b},array:function(){return a.value.length>b},other:function(){return a.value>b}})}},{name:"lessEquals",count:1,type:"query",method:function(a,b){b=a.helper.when(b,{number:function(){return b},date:function(){return b},other:function(){return b.length}});return a.when({string:function(){return a.value.length<=
b},array:function(){return a.value.length<=b},other:function(){return a.value<=b}})}},{name:"greaterEquals",count:1,type:"query",method:function(a,b){b=a.helper.when(b,{number:function(){return b},date:function(){return b},other:function(){return b.length}});return a.when({string:function(){return a.value.length>=b},array:function(){return a.value.length>=b},other:function(){return a.value>=b}})}},{name:"between",count:2,type:"query",method:function(a,b,c){b=a.helper.when(b,{number:function(){return b},
date:function(){return value},other:function(){return b.length}});c=a.helper.when(c,{number:function(){return c},other:function(){return c.length}});return a.when({string:function(){return a.value.length>b&&a.value.length<c},array:function(){return a.value.length>b&&a.value.length<c},other:function(){return a.value>b&&a.value<c}})}},{name:"betweenEquals",count:2,type:"query",method:function(a,b,c){b=a.helper.when(b,{number:function(){return b},date:function(){return value},other:function(){return b.length}});
c=a.helper.when(c,{number:function(){return c},date:function(){return value},other:function(){return c.length}});return a.when({string:function(){return a.value.length>=b&&a.value.length<=c},array:function(){return a.value.length>=b&&a.value.length<=c},other:function(){return a.value>=b&&a.value<=c}})}},{name:"empty",count:0,type:"query",method:function(a){return a.when({array:function(){return a.value.length==0},string:function(){return a.value==""},empty:function(){return true}})}},{name:"is",count:0,
type:"query",method:function(a){return a.when({bool:function(){return a.value},empty:function(){return false},other:function(){return a.value!=null}})}},{name:"isNot",count:0,type:"query",method:function(a){return a.when({bool:function(){return!a.value},empty:function(){return true},other:function(){return a.value==null}})}},{name:"any",type:"selection",method:function(a){return a.results.selected.length>0}},{name:"all",type:"selection",method:function(a){return a.results.selected.length==a.state.data.length}},
{name:"none",type:"selection",method:function(a){return!a.query.all()}},{name:"count",type:"selection",method:function(a,b){return b?a.results.remaining.length:a.results.selected.length}},{name:"select",type:"selection",method:function(a,b,c){var g=[];c=c?a.results.remaining:a.results.selected;b=a.helper.type(b)=="function"?b:function(d){return d};for(a=0;a<c.length;a++)g.push(b(c[a]));return g}},{name:"toTable",type:"selection",manual:true,method:function(a,b,c,g){b=b?b:{};c=a.query.select(c,g);
if(c.count==0)return"No results for this query";g=function(i){a.helper.when(i,{date:function(){i=a.helper.format("%0%/%1%/%2% at %3%:%4% %5%",[i.getMonth()+1,i.getDate(),i.getFullYear(),i.getHours()>12?i.getHours()-12:i.getHours(),i.getMinutes(),i.getHours()>12?"PM":"AM"])},empty:function(){i="null"},other:function(){i=i.toString()}});return i};b=["<table cellpadding='0' cellspacing='0' "+(b.border?"border='"+b.border+"' ":"")+(b.css?"class='"+b.css+"' ":"")+" >"];if(a.state.useProperties){var d=
[];b.push("<tr>");for(var h in c[0]){d.push(h);b.push("<th>");b.push(escape(h));b.push("</th>")}b.push("</tr>")}for(var e=true,p=0;p<c.length;p++){e=!e;var f=c[p];b.push("<tr "+(e?"class='alt-row'":"")+">");if(a.state.useProperties)for(var j in d){h=d[j];h=g(f[h]);b.push("<td>");b.push(h);b.push("</td>")}else{b.push("<td>");b.push(g(f));b.push("</td>")}b.push("</tr>")}b.push("</table>");return b.join("")}},{name:"each",type:"selection",manual:true,method:function(a,b,c,g){c=a.query.select(c,g);for(g=
0;g<c.length;g++)b(c[g],g);return a.query}},{name:"orderBy",type:"selection",manual:true,method:function(a,b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z){b=a.helper.all([b,c,g,d,h,e,p,f,j,i,l,k,m,n,o,r,q,s,t,u,v,w,x,y,z]);if(b.length==0)b=[""];if(!a.state.useProperties){b=b.length>0?(b[0]+"").match(/^\-/g):false;a.state.data=a.helper.sort(a.state.data,null,b);return a.query}c=[];for(g=0;g<b.length;g++)c.push({desc:b[g].substr(0,1)=="-",field:b[g].replace(/^\-/g,"")});a.state.data=a.helper.sort(a.state.data,
c);return a.query}},{name:"distinct",type:"selection",method:function(a,b,c){b=a.helper.distinct(c?a.results.remaining:a.results.selected,b);c=[];for(var g in b)c.push(b[g].key);return a.helper.sort(c,null,false)}},{name:"groupBy",type:"selection",method:function(a,b,c){a=a.helper.distinct(c?a.results.remaining:a.results.selected,b);return jLinq.from(a)}},{name:"join",type:"selection",method:function(a,b,c,g,d){b=a.helper.clone(b);for(var h=[],e=0;e<a.state.data.length;e++){var p=a.helper.clone(a.state.data[e]),
f=jLinq.from(b).equals(d,p[g]).select();if(f.length==1)p[c]=f[0];else p[e][c]=f;h.push(p)}return jLinq.from(h)}},{name:"attach",type:"selection",method:function(a,b,c){for(var g=0;g<a.state.data.length;g++)a.state.data[g][b]=c(a.state.data[g])}},{name:"skipTake",type:"selection",manual:true,method:function(a,b,c,g,d){b=Math.max(a.helper.type(b)=="number"?b:0,0);c=Math.max(a.helper.type(c)=="number"?c:0,0);return a.query.select(g,d).slice(b,b+c)}},{name:"take",type:"selection",manual:true,method:function(a,
b,c,g){b=Math.max(a.helper.type(b)=="number"?b:0,0);return a.query.select(c,g).slice(0,b)}},{name:"first",type:"selection",manual:true,method:function(a,b,c,g){a=a.query.select(c,g);return a.length>0?a[0]:b?b:null}},{name:"last",type:"selection",manual:true,method:function(a,b,c,g){a=a.query.select(c,g);return a.length>0?a[a.length-1]:b?b:null}},{name:"at",type:"selection",manual:true,method:function(a,b,c,g,d){a=a.query.select(g,d);return b<a.length||b>=0?a[b]:c?c:null}},{name:"sum",type:"selection",
method:function(a,b,c){a.state.useProperties||(c=b);c=c?a.results.remaining:a.results.selected;var g=0;a.helper.each(c,function(d){if(a.state.useProperties)if(g==null)g=d[b];else a.helper.when(d[b],{array:function(){g+=d[b].length},string:function(){g+=d[b].length},other:function(){g+=d[b]}});else a.helper.when(d,{array:function(){g+=d.length},string:function(){g+=d.length},other:function(){g+=d}})});return{count:c.length,result:g,records:c}}},{name:"average",type:"selection",method:function(a,b,
c){a=c?a.results.remaining:a.results.selected;b=jLinq.from(a).sum(b).result;return{total:b,count:a.length,result:b/a.length,records:a}}},{name:"max",type:"selection",method:function(a,b,c){c=jLinq.from(c?a.results.remaining:a.results.selected).select(function(g){g=a.state.useProperties?g[b]:g;return{value:g,count:a.helper.getNumericValue(g)}});return jLinq.from(c).orderBy("count","value").last().value}},{name:"min",type:"selection",method:function(a,b,c){c=jLinq.from(c?a.results.remaining:a.results.selected).select(function(g){g=
a.state.useProperties?g[b]:g;return{value:g,count:a.helper.getNumericValue(g)}});return jLinq.from(c).orderBy("count","value").first().value}},{name:"except",type:"selection",method:function(a,b,c){c=c?a.results.remaining:a.results.selected;if(!(b&&b.length&&b.length>0))return jLinq.from(c);c=jLinq.from(c).notWhere(function(g){for(var d=0;d<b.length;d++)if(a.state.useProperties){if(a.helper.propsEqual(b[d],g))return true}else if(a.helper.equals(b[d],g))return true;return false}).select();return jLinq.from(c)}},
{name:"intersect",type:"selection",method:function(a,b,c){c=c?a.results.remaining:a.results.selected;if(!(b&&b.length&&b.length>0))return jLinq.from(c);c=jLinq.from(c).where(function(g){for(var d=0;d<b.length;d++)if(a.state.useProperties){if(a.helper.propsEqual(b[d],g))return true}else if(a.helper.equals(b[d],g))return true;return false}).select();return jLinq.from(c)}},{name:"union",type:"selection",method:function(a,b,c){c=c?a.results.remaining:a.results.selected;if(!(b&&b.length&&b.length>0))return jLinq.from(c);
return jLinq.from(b.concat(jLinq.from(c).where(function(g){for(var d=0;d<b.length;d++)if(a.state.useProperties){if(a.helper.propsEqual(b[d],g))return false}else if(a.helper.equals(b[d],g))return false;return true}).select()))}},{name:"skipWhile",type:"selection",method:function(a,b,c){var g=true;return jLinq.from(c?a.results.remaining:a.results.selected).where(function(d,h){if(g)g=b(d,h);return!g}).select()}},{name:"takeWhile",type:"selection",method:function(a,b,c){var g=true;return jLinq.from(c?
a.results.remaining:a.results.selected).where(function(d){if(g)g=b(d,a.helper);return g}).select()}},{name:"selectMany",type:"selection",method:function(a,b,c,g,d){d=d?a.results.remaining:a.results.selected;g=g?g:function(e,p){return{source:e,compare:p}};var h=[];a.helper.each(d,function(e){a.helper.each(b,function(p){c(e,p)&&h.push(g(e,p))})});return h}}]}};jLinq=new Q(R());jLinq.finish(true);jLinq.library=function(a,b){if(b==null)b=true;var c=new Q(R());if(!b){c.types={};c.extend=[]}b=false;if(a){if(a.extend)for(var g in a.extend)c.extend(a.extend[g]);
if(a.types)for(var d in a.types)c.addType(a.types[d]);if(a.locked)b=a.locked}c.finish(b);return c}})();
