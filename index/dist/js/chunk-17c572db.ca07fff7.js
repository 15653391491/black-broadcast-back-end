(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-17c572db"],{"113b":function(e,t,a){"use strict";a("d3b7")},"406b":function(e,t,a){},aae8:function(e,t,a){"use strict";a("406b")},c6c8:function(e,t,a){"use strict";a("d2e5")},d2e5:function(e,t,a){},d3b7:function(e,t,a){},fa8c:function(e,t,a){"use strict";a.r(t);var l=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("el-container",[a("el-header",[a("Header",{attrs:{collapseFlag:e.collapseFlag,currOptionNum:e.currOptionNum},on:{backToScreen:e.backToScreen,menuCollapse:e.menuCollapse,tabChanged:e.tabChanged}})],1),a("el-container",[a("el-aside",{staticStyle:{width:"auto"}},[a("Menu",{attrs:{mode:"vertical",collapseFLag:e.collapseFlag},on:{menuChange:e.menuChange}})],1),a("el-main",[a("router-view",{attrs:{currTabNum:e.currTabNum}})],1)],1)],1)},n=[],o=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("el-menu",{staticClass:"el-menu-demo",attrs:{"default-active":e.activeIndex,mode:e.mode,"background-color":e.backgroundColor,"text-color":e.textColor,"active-text-color":e.activeTextColor,"collapse-transition":!0,collapse:e.isCollapse},on:{select:e.handleSelect}},[a("el-menu-item",{attrs:{index:"bigData"}},[a("i",{staticClass:"el-icon-data-line",staticStyle:{"margin-right":"24px"}}),a("span",{staticClass:"itemtitle",attrs:{slot:"title"},slot:"title"},[e._v("大数据分析")])]),a("el-menu-item",{attrs:{index:"broad"}},[a("i",{staticClass:"el-icon-microphone",staticStyle:{"margin-right":"24px"}}),a("span",{attrs:{slot:"title"},slot:"title"},[e._v("黑广播查询")])]),a("el-menu-item",{attrs:{index:"work"}},[a("i",{staticClass:"el-icon-s-order",staticStyle:{"margin-right":"24px"}}),a("span",{attrs:{slot:"title"},slot:"title"},[e._v("工作管理")])])],1)},c=[],i={data:function(){return{activeIndex:"1",isCollapse:!1}},props:{mode:{type:String,default:"horizontal"},backgroundColor:{type:String,default:"rgb(255, 255, 255)"},textColor:{type:String,default:"rgb(90, 84, 84)"},activeTextColor:{type:String,default:"rgb(109, 97, 234)"},collapseFLag:{type:Boolean,default:!1}},watch:{collapseFLag:function(){this.isCollapse=!this.isCollapse}},methods:{handleSelect:function(e){this.$router.push({name:e}),this.$emit("menuChange",e)}}},s=i,r=(a("aae8"),a("2877")),u=Object(r["a"])(s,o,c,!1,null,null,null),m=u.exports,p=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("a",{staticClass:"backToScreenA",staticStyle:{float:"left"},on:{click:e.backToScreen}},[a("i",{staticClass:"el-icon-monitor backToScreenStyle"}),a("span",{staticClass:"backToScreenStyle"},[e._v("返回大屏")])]),a("a",{staticStyle:{float:"left"},on:{click:e.menuCollapse}},[a("i",{class:{"el-icon-s-unfold":!e.collapseFlag,"el-icon-s-fold":e.collapseFlag,collapseIcon:!0}})]),a("router-view",{staticStyle:{float:"left","margin-left":"2vw"},attrs:{name:"tabs"},on:{tabChanged:e.tabChanged}})],1)},d=[],b={methods:{menuCollapse:function(){this.$emit("menuCollapse")},backToScreen:function(){this.$emit("backToScreen")},tabChanged:function(e){this.$emit("tabChanged",e)}},props:{collapseFlag:{type:Boolean,default:!1},currOptionNum:{type:Number,default:2}},computed:{title:function(){var e="";switch(this.currOptionNum){case 1:e="大数据分析";break;case 2:e="黑广播查询";break;case 3:e="工作管理";break;case 4:e="控制中心";break;default:break}return e}}},h=b,f=(a("c6c8"),Object(r["a"])(h,p,d,!1,null,null,null)),g=f.exports,C={components:{Menu:m,Header:g},data:function(){return{collapseFlag:!1,currOptionNum:1,currTabNum:1,currPageNum:1}},methods:{menuCollapse:function(){this.collapseFlag=!this.collapseFlag},menuChange:function(e){this.currOptionNum=Number(e),this.currPageNum=Number(e),this.currTabNum=1,"work"===e&&(location.replace("#/work"),location.reload())},tabChanged:function(e){this.currTabNum=Number(e)},backToScreen:function(){this.$router.push({name:"index"})}}},k=C,S=(a("113b"),Object(r["a"])(k,l,n,!1,null,null,null));t["default"]=S.exports}}]);
//# sourceMappingURL=chunk-17c572db.ca07fff7.js.map