(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-17c572db"],{"113b":function(t,e,a){"use strict";a("d3b7")},"406b":function(t,e,a){},aae8:function(t,e,a){"use strict";a("406b")},c6c8:function(t,e,a){"use strict";a("d2e5")},d2e5:function(t,e,a){},d3b7:function(t,e,a){},fa8c:function(t,e,a){"use strict";a.r(e);var l=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("el-container",[a("el-header",[a("Header",{attrs:{collapseFlag:t.collapseFlag,currOptionNum:t.currOptionNum},on:{backToScreen:t.backToScreen,menuCollapse:t.menuCollapse,tabChanged:t.tabChanged}})],1),a("el-container",[a("el-aside",{staticStyle:{width:"auto"}},[a("Menu",{attrs:{mode:"vertical",collapseFLag:t.collapseFlag},on:{menuChange:t.menuChange}})],1),a("el-main",[a("keep-alive",[a("router-view",{attrs:{currTabNum:t.currTabNum}})],1)],1)],1)],1)},n=[],o=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("el-menu",{staticClass:"el-menu-demo",attrs:{"default-active":t.activeIndex,mode:t.mode,"background-color":t.backgroundColor,"text-color":t.textColor,"active-text-color":t.activeTextColor,"collapse-transition":!0,collapse:t.isCollapse},on:{select:t.handleSelect}},[a("el-menu-item",{attrs:{index:"bigData"}},[a("i",{staticClass:"el-icon-data-line",staticStyle:{"margin-right":"24px"}}),a("span",{staticClass:"itemtitle",attrs:{slot:"title"},slot:"title"},[t._v("大数据分析")])]),a("el-menu-item",{attrs:{index:"broad"}},[a("i",{staticClass:"el-icon-microphone",staticStyle:{"margin-right":"24px"}}),a("span",{attrs:{slot:"title"},slot:"title"},[t._v("黑广播查询")])]),a("el-menu-item",{attrs:{index:"work"}},[a("i",{staticClass:"el-icon-s-order",staticStyle:{"margin-right":"24px"}}),a("span",{attrs:{slot:"title"},slot:"title"},[t._v("工作管理")])])],1)},c=[],s={data:function(){return{activeIndex:"1",isCollapse:!1}},props:{mode:{type:String,default:"horizontal"},backgroundColor:{type:String,default:"rgb(255, 255, 255)"},textColor:{type:String,default:"rgb(90, 84, 84)"},activeTextColor:{type:String,default:"rgb(109, 97, 234)"},collapseFLag:{type:Boolean,default:!1}},watch:{collapseFLag:function(){this.isCollapse=!this.isCollapse}},methods:{handleSelect:function(t){this.$router.push({name:t}),this.$emit("menuChange",t)}}},i=s,r=(a("aae8"),a("2877")),u=Object(r["a"])(i,o,c,!1,null,null,null),p=u.exports,m=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",[a("a",{staticClass:"backToScreenA",staticStyle:{float:"left"},on:{click:t.backToScreen}},[a("i",{staticClass:"el-icon-monitor backToScreenStyle"}),a("span",{staticClass:"backToScreenStyle"},[t._v("返回大屏")])]),a("a",{staticStyle:{float:"left"},on:{click:t.menuCollapse}},[a("i",{class:{"el-icon-s-unfold":!t.collapseFlag,"el-icon-s-fold":t.collapseFlag,collapseIcon:!0}})]),a("router-view",{staticStyle:{float:"left","margin-left":"2vw"},attrs:{name:"tabs"},on:{tabChanged:t.tabChanged}}),a("span",{staticClass:"title"},[t._v(t._s(t.title))])],1)},d=[],b={methods:{menuCollapse:function(){this.$emit("menuCollapse")},backToScreen:function(){this.$emit("backToScreen")},tabChanged:function(t){this.$emit("tabChanged",t)}},props:{collapseFlag:{type:Boolean,default:!1},currOptionNum:{type:Number,default:2}},computed:{title:function(){var t="";switch(this.currOptionNum){case 1:t="大数据分析";break;case 2:t="黑广播查询";break;case 3:t="工作管理";break;case 4:t="控制中心";break;default:break}return t}}},h=b,f=(a("c6c8"),Object(r["a"])(h,m,d,!1,null,null,null)),g=f.exports,C={components:{Menu:p,Header:g},data:function(){return{collapseFlag:!1,currOptionNum:1,currTabNum:1,currPageNum:1}},methods:{menuCollapse:function(){this.collapseFlag=!this.collapseFlag},menuChange:function(t){this.currOptionNum=Number(t),this.currPageNum=Number(t),this.currTabNum=1},tabChanged:function(t){this.currTabNum=Number(t)},backToScreen:function(){this.$router.push({name:"index"})}}},k=C,S=(a("113b"),Object(r["a"])(k,l,n,!1,null,null,null));e["default"]=S.exports}}]);
//# sourceMappingURL=chunk-17c572db.e7a8b3cd.js.map