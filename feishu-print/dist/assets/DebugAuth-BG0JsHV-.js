import{d as g,u as f,r as o,o as m,c as k,b as s,t as a,j as _,_ as y}from"./index-mInWaxl3.js";import{t as S}from"./templates-DCFN9nDS.js";const b={class:"debug-page"},$={class:"section"},h={class:"section"},I={class:"section"},N={class:"section"},T=g({__name:"DebugAuth",setup(A){const{initUser:c,userStatus:p}=f(),u=o(""),n=o(""),l=o(""),r=o(""),i=()=>{const e=localStorage.getItem("session_token");e?u.value=`✅ Token 存在
长度: ${e.length}
前50字符: ${e.substring(0,50)}...`:u.value="❌ Token 不存在"},d=async()=>{var e;n.value="正在初始化...";try{const t=await c();n.value=`✅ 初始化成功
${JSON.stringify(t,null,2)}`,i()}catch(t){n.value=`❌ 初始化失败
${t.message}
${JSON.stringify((e=t.response)==null?void 0:e.data,null,2)}`}},v=async()=>{var e;l.value="正在获取...";try{const t=await S.getAll(void 0,"ai");l.value=`✅ 获取成功
共 ${t.length} 个模板
${JSON.stringify(t.slice(0,3),null,2)}`}catch(t){l.value=`❌ 获取失败
${t.message}
${JSON.stringify((e=t.response)==null?void 0:e.data,null,2)}`}};return m(()=>{i(),r.value=JSON.stringify(p.value,null,2)}),(e,t)=>(_(),k("div",b,[t[4]||(t[4]=s("h1",null,"认证调试页面",-1)),s("div",$,[t[0]||(t[0]=s("h2",null,"1. 检查 Session Token",-1)),s("button",{onClick:i},"检查 Token"),s("pre",null,a(u.value),1)]),s("div",h,[t[1]||(t[1]=s("h2",null,"2. 初始化用户",-1)),s("button",{onClick:d},"初始化用户"),s("pre",null,a(n.value),1)]),s("div",I,[t[2]||(t[2]=s("h2",null,"3. 测试获取模板",-1)),s("button",{onClick:v},"获取 AI 模板"),s("pre",null,a(l.value),1)]),s("div",N,[t[3]||(t[3]=s("h2",null,"4. 用户状态",-1)),s("pre",null,a(r.value),1)])]))}}),C=y(T,[["__scopeId","data-v-69b3473d"]]);export{C as default};
