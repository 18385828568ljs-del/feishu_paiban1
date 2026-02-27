import{d as Z,r as p,N as tt,o as et,a as at,O as W,c as r,b as a,f as R,g as nt,t as m,C as $,e as ot,j as l,_ as st}from"./index-mInWaxl3.js";import{s as O}from"./signature-DGkbQbJ4.js";const it={class:"signature-page"},rt={class:"signature-container"},lt={key:0,class:"loading-state"},dt={key:1,class:"error-state"},ct={key:2,class:"signed-state"},ut={class:"signature-preview"},pt=["src"],ht={key:3,class:"pending-state"},vt={class:"header"},mt={class:"subtitle"},gt={class:"signer-info"},ft={class:"info-item"},wt={class:"value"},bt={class:"info-item"},xt={class:"value"},kt={key:0,class:"document-preview"},_t={class:"preview-header"},yt={key:0,class:"preview-viewport"},Ct={class:"signature-area"},Mt={class:"canvas-wrapper"},Tt={key:0,class:"placeholder"},Dt={class:"actions"},St=["disabled"],Bt={key:0},Pt={key:1},Rt=Z({__name:"SignaturePage",setup(Ht){const I=at(),T=p(!0),x=p(""),s=p(null),D=p(!1),k=p(!0),N=p(null),z=()=>{var d;const e=N.value;if(!e||!((d=s.value)!=null&&d.document_html))return;const t=s.value.document_html,b=`<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: sans-serif;
    font-size: 14px;
    color: #1e293b;
    background: #f1f5f9;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 0;
  }
  #template-root {
    width: 100% !important;
    min-height: auto !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
  }
  .template-page-content {
    width: 210mm;
    min-height: 297mm;
    background: #fff;
    padding: 10mm;
    box-sizing: border-box;
    margin: 8px auto;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    position: relative;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  .template-page-content img { max-width: 100%; height: auto; }
  .template-page-content table { max-width: 100%; border-collapse: collapse; }
  .template-page-content td, .template-page-content th { border: 1px solid #94a3b8; padding: 0.5rem; }
  .template-page-content th { background: #e2e8f0; font-weight: 600; }
  .template-field.is-mapped { display: none !important; }
  .mapped-shadow { display: inline; line-height: inherit; }
  p.mapped-shadow { display: block; }
  .template-field { padding: 0 2px; border-radius: 2px; color: #1e40af; background: #dbeafe; }
  /* 隐藏编辑器辅助元素 */
  .mce-pagebreak, .page-break-visual { display: none; }
</style>
</head>
<body>${t.includes("template-page-content")?t:`<div id="template-root"><div class="template-page-content">${t}</div></div>`}</body>
</html>`,c=e.contentDocument;if(!c)return;c.open(),c.write(b),c.close();const i=()=>{var u;if(!((u=e.contentDocument)!=null&&u.body))return;const h=e.contentDocument.body.scrollHeight;e.style.height=h+"px"};setTimeout(i,50),setTimeout(i,300),setTimeout(i,1e3)};tt(k,async e=>{e&&(await W(),z())});const _=p(null);let o=null,y=!1,g=0,f=0;const w=p(!0),E=e=>e?new Date(e).toLocaleString("zh-CN"):"-";et(async()=>{var t,n;const e=I.params.token;if(!e){x.value="无效的签名链接",T.value=!1;return}try{s.value=await O.getByToken(e),T.value=!1,s.value.status==="pending"&&(await W(),U(),z())}catch(C){x.value=((n=(t=C.response)==null?void 0:t.data)==null?void 0:n.detail)||"签名链接无效或已过期",T.value=!1}});const U=()=>{const e=_.value;if(!e)return;const t=e.parentElement;t&&(e.width=t.clientWidth,e.height=t.clientHeight,o=e.getContext("2d"),o&&(o.lineCap="round",o.lineJoin="round",o.strokeStyle="#000000",o.lineWidth=2))},S=e=>{const t=_.value;if(!t)return{x:0,y:0};const n=t.getBoundingClientRect();return{x:e.clientX-n.left,y:e.clientY-n.top}},A=e=>{y=!0;const{x:t,y:n}=S(e);g=t,f=n},J=e=>{if(!y||!o)return;const{x:t,y:n}=S(e);o.beginPath(),o.moveTo(g,f),o.lineTo(t,n),o.stroke(),g=t,f=n,w.value=!1},H=()=>{y=!1},q=e=>{if(e.touches.length===1){y=!0;const{x:t,y:n}=S(e.touches[0]);g=t,f=n}},F=e=>{if(!y||!o||e.touches.length!==1)return;const{x:t,y:n}=S(e.touches[0]);o.beginPath(),o.moveTo(g,f),o.lineTo(t,n),o.stroke(),g=t,f=n,w.value=!1},G=()=>{const e=_.value;!e||!o||(o.clearRect(0,0,e.width,e.height),w.value=!0)},K=async()=>{var L,X;const e=_.value;if(!e||w.value||!s.value||!o)return;const t=I.params.token,n=o.getImageData(0,0,e.width,e.height),{data:C,width:b,height:c}=n;let i=b,d=c,h=0,u=0;for(let v=0;v<c;v++)for(let M=0;M<b;M++)C[(v*b+M)*4+3]>0&&(i=Math.min(i,M),d=Math.min(d,v),h=Math.max(h,M),u=Math.max(u,v));const B=5;i=Math.max(0,i-B),d=Math.max(0,d-B),h=Math.min(b,h+B),u=Math.min(c,u+B);const V=h-i,j=u-d,P=document.createElement("canvas");P.width=V,P.height=j;const Y=P.getContext("2d");Y&&Y.drawImage(e,i,d,V,j,0,0,V,j);const Q=P.toDataURL("image/png");D.value=!0;try{s.value=await O.submit(t,Q)}catch(v){x.value=((X=(L=v.response)==null?void 0:L.data)==null?void 0:X.detail)||"提交签名失败"}finally{D.value=!1}};return(e,t)=>{var n;return l(),r("div",it,[a("div",rt,[T.value?(l(),r("div",lt,t[1]||(t[1]=[a("div",{class:"spinner"},null,-1),a("p",null,"正在加载签名请求...",-1)]))):x.value?(l(),r("div",dt,[t[2]||(t[2]=nt('<div class="error-icon" data-v-f90714d0><svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-v-f90714d0><circle cx="12" cy="12" r="10" data-v-f90714d0></circle><path d="m15 9-6 6" data-v-f90714d0></path><path d="m9 9 6 6" data-v-f90714d0></path></svg></div>',1)),a("h2",null,m(x.value),1),t[3]||(t[3]=a("p",null,"请联系发送方获取新的签名链接",-1))])):((n=s.value)==null?void 0:n.status)==="signed"?(l(),r("div",ct,[t[4]||(t[4]=a("div",{class:"success-icon"},[a("svg",{xmlns:"http://www.w3.org/2000/svg",width:"64",height:"64",viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":"2","stroke-linecap":"round","stroke-linejoin":"round"},[a("circle",{cx:"12",cy:"12",r:"10"}),a("path",{d:"m9 12 2 2 4-4"})])],-1)),t[5]||(t[5]=a("h2",null,"签名已完成",-1)),a("p",null,"签名人："+m(s.value.signer_name),1),a("p",null,"签名时间："+m(E(s.value.signed_at)),1),a("div",ut,[a("img",{src:s.value.signature_data,alt:"签名"},null,8,pt)])])):s.value?(l(),r("div",ht,[a("div",vt,[t[6]||(t[6]=a("h1",null,"电子签名",-1)),a("p",mt,m(s.value.document_title||"请在下方完成签名"),1)]),a("div",gt,[a("div",ft,[t[7]||(t[7]=a("span",{class:"label"},"签名人",-1)),a("span",wt,m(s.value.signer_name),1)]),a("div",bt,[t[8]||(t[8]=a("span",{class:"label"},"有效期至",-1)),a("span",xt,m(E(s.value.expires_at)),1)])]),s.value.document_html?(l(),r("div",kt,[a("div",_t,[t[9]||(t[9]=a("svg",{xmlns:"http://www.w3.org/2000/svg",width:"16",height:"16",viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":"2","stroke-linecap":"round","stroke-linejoin":"round"},[a("path",{d:"M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"}),a("polyline",{points:"14 2 14 8 20 8"})],-1)),t[10]||(t[10]=a("span",null,"文档预览",-1)),a("button",{class:"btn-toggle",onClick:t[0]||(t[0]=C=>k.value=!k.value)},m(k.value?"收起":"展开"),1)]),k.value?(l(),r("div",yt,[a("iframe",{ref_key:"previewIframeRef",ref:N,class:"preview-iframe",sandbox:"allow-same-origin",frameborder:"0",scrolling:"no"},null,512)])):R("",!0)])):R("",!0),a("div",Ct,[a("div",Mt,[a("canvas",{ref_key:"canvasRef",ref:_,onMousedown:A,onMousemove:J,onMouseup:H,onMouseleave:H,onTouchstart:$(q,["prevent"]),onTouchmove:$(F,["prevent"]),onTouchend:H},null,544),w.value?(l(),r("div",Tt," 请在此处签名 ")):R("",!0)])]),a("div",Dt,[a("button",{class:"btn btn-secondary",onClick:G},t[11]||(t[11]=[a("svg",{xmlns:"http://www.w3.org/2000/svg",width:"18",height:"18",viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":"2","stroke-linecap":"round","stroke-linejoin":"round"},[a("path",{d:"M3 6h18"}),a("path",{d:"M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"}),a("path",{d:"M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"})],-1),ot(" 清除 ")])),a("button",{class:"btn btn-primary",onClick:K,disabled:w.value||D.value},[D.value?(l(),r("span",Bt,"提交中...")):(l(),r("span",Pt,"确认签名"))],8,St)])])):R("",!0)])])}}}),Nt=st(Rt,[["__scopeId","data-v-f90714d0"]]);export{Nt as default};
