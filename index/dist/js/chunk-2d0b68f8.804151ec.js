(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0b68f8"],{"1e4b":function(e,a,t){"use strict";t.r(a);var n=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("el-tabs",{on:{"tab-click":e.handleClick},model:{value:e.activeName,callback:function(a){e.activeName=a},expression:"activeName"}},e._l(e.tabOptions,(function(e){return t("el-tab-pane",{key:e.name,attrs:{label:e.label,name:e.name}})})),1)},l=[],i={data:function(){return{activeName:"1",bigDataOptions:[{label:"时间分布",name:"1"},{label:"内容分布",name:"2"},{label:"空间分布",name:"3"}],broadCastOptions:[{label:"条件查询",name:"1"},{label:"区域查询",name:"2"}],workOptions:[{label:"终端管理",name:"1"},{label:"频点分类管理",name:"2"},{label:"人员管理",name:"3"},{label:"使用记录",name:"4"}],controlOptions:[{label:"系统设置",name:"1"},{label:"配置信息",name:"2"}]}},props:{currOptionNum:{type:Number,default:2}},watch:{currOptionNum:function(){}},computed:{tabOptions:function(){switch(2){case 1:return this.bigDataOptions;case 2:return this.broadCastOptions;case 3:return this.workOptions;case 4:return this.controlOptions;default:return[]}}},methods:{handleClick:function(){this.$emit("tabChanged",this.activeName)}}},o=i,c=t("2877"),s=Object(c["a"])(o,n,l,!1,null,"5b4e2514",null);a["default"]=s.exports}}]);
//# sourceMappingURL=chunk-2d0b68f8.804151ec.js.map