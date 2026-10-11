(function(){
const NS='http://www.w3.org/2000/svg';
const n0=d3.format(',.0f'),pct1=(v)=>d3.format('.1f')(v)+'%',pct0=(v)=>d3.format('.0f')(v)+'%';
const cmp=new Intl.NumberFormat('en',{notation:'compact',maximumFractionDigits:1});
const signed=(v)=>(v>0?'+':v<0?'−':'')+Math.abs(v).toFixed(1)+'%';
const $=(id)=>document.getElementById(id);
const MONTHS=['','January','February','March','April','May','June','July','August','September','October','November','December'];
const state={pay:'All',st:'All',vk:'State',tab:'findings'};
const TABS=['findings','typical','variation','people','health'];
const C=(i)=>dash.colors[i];
const MUTED='var(--cds-chart-muted,#9a9a95)',GRID='var(--cds-chart-grid,rgba(128,128,128,.22))',AXIS='var(--cds-chart-axis,#8a8a85)',REF='var(--cds-chart-reference,#8a8a85)';
const get=(id)=>{const d=dash.data(id);return d.status==='ok'?d.data:null;};

/* ---------- small drawing helpers ---------- */
function frame(box,H,minW){box.textContent='';box.classList.remove('dash-skeleton');const W=Math.max(box.clientWidth||320,minW||280);
  const svg=d3.select(box).append('svg').attr('viewBox',`0 0 ${W} ${H}`).attr('role','img');return {svg,W,H};}
function textW(svg,str,size){const t=svg.append('text').attr('font-size',size||11).attr('opacity',0).text(str);const w=t.node().getComputedTextLength();t.remove();return w;}
function msg(box,text){box.textContent='';box.classList.remove('dash-skeleton');const p=document.createElement('div');p.className='fail';const i=document.createElement('i');p.append(i,document.createTextNode(text));box.appendChild(p);}
function tipper(box){let tip=box.querySelector('.tip');if(!tip){tip=document.createElement('div');tip.className='tip';tip.hidden=true;box.appendChild(tip);}
  return {show(x,y,title,rows){tip.textContent='';const t=document.createElement('div');t.className='t';t.textContent=title;tip.appendChild(t);
      rows.forEach(r=>{const d=document.createElement('div');d.className='r';if(r.color){const s=document.createElement('i');s.style.background=r.color;d.appendChild(s);}d.appendChild(document.createTextNode(r.text));tip.appendChild(d);});
      tip.hidden=false;const bw=box.clientWidth,tw=tip.offsetWidth;tip.style.left=Math.max(0,Math.min(bw-tw,x+12))+'px';tip.style.top=Math.max(0,y-8)+'px';},
    hide(){tip.hidden=true;}};}
function legend(id,items){const lg=$(id);lg.textContent='';items.forEach(it=>{const sp=document.createElement('span');const i=document.createElement('i');i.style.background=it.color;if(it.ring){i.style.background='transparent';i.style.border='2px solid '+it.color;i.style.borderRadius='50%';}sp.append(i,document.createTextNode(it.name));lg.appendChild(sp);});}
function yAxis(g,y,W,left,right,fmtv,ticks){y.ticks(ticks||4).forEach(t=>{g.append('line').attr('x1',left).attr('x2',W-right).attr('y1',y(t)).attr('y2',y(t)).attr('stroke',GRID);
  g.append('text').attr('x',left-6).attr('y',y(t)+4).attr('text-anchor','end').text(fmtv(t));});}

/* ---------- line chart ---------- */
function lineChart(box,series,o){
  const H=o.height||260,left=o.left||50,right=14,top=12,bot=28;const {svg,W}=frame(box,H);
  const xs=series.flatMap(s=>s.pts.map(p=>+p.x)),x0=d3.min(xs),x1=d3.max(xs);
  const isDate=o.date;const x=(isDate?d3.scaleUtc():d3.scaleLinear()).domain(isDate?[new Date(x0),new Date(x1)]:[x0,x1]).range([left,W-right]);
  const ymax=d3.max(series,s=>d3.max(s.pts,p=>p.y))||1,y=d3.scaleLinear().domain([0,ymax*1.06]).nice().range([H-bot,top]);
  yAxis(svg,y,W,left,right,o.yfmt,4);
  const xt=isDate?x.ticks(Math.max(3,Math.floor(W/110))):(o.xticks||x.ticks(Math.max(3,Math.floor(W/90))));
  xt.forEach(t=>{svg.append('text').attr('x',x(t)).attr('y',H-8).attr('text-anchor','middle').text(isDate?d3.utcFormat('%Y')(t):o.xfmt(t));});
  svg.append('line').attr('x1',left).attr('x2',W-right).attr('y1',H-bot).attr('y2',H-bot).attr('stroke',AXIS);
  (o.refs||[]).forEach(r=>{svg.append('line').attr('x1',left).attr('x2',W-right).attr('y1',y(r.y)).attr('y2',y(r.y)).attr('stroke',REF).attr('stroke-dasharray','4 4');
    if(r.label)svg.append('text').attr('x',left+4).attr('y',y(r.y)-4).text(r.label);});
  const px=(p)=>x(isDate?new Date(p.x):p.x);
  series.forEach(s=>{const full=s.pts.filter(p=>!p.partial),line=d3.line().x(px).y(p=>y(p.y));
    svg.append('path').attr('d',line(full)).attr('fill','none').attr('stroke',s.color).attr('stroke-width',2).attr('stroke-linejoin','round').attr('stroke-linecap','round');
    const part=s.pts.filter(p=>p.partial);
    if(part.length&&full.length){svg.append('path').attr('d',line([full[full.length-1],...part])).attr('fill','none').attr('stroke',s.color).attr('stroke-width',2).attr('stroke-dasharray','3 3');}
    if(o.dots)s.pts.forEach(p=>svg.append('circle').attr('cx',px(p)).attr('cy',y(p.y)).attr('r',3.2).attr('fill',p.partial?'var(--color-panel)':s.color).attr('stroke',s.color).attr('stroke-width',1.5));});
  const tip=tipper(box),cross=svg.append('line').attr('y1',top).attr('y2',H-bot).attr('stroke',AXIS).attr('opacity',0);
  const all=[...new Set(series.flatMap(s=>s.pts.map(p=>+p.x)))].sort((a,b)=>a-b);
  svg.append('rect').attr('x',left).attr('y',top).attr('width',W-left-right).attr('height',H-bot-top).attr('fill','transparent')
    .on('pointermove',(ev)=>{const [mx]=d3.pointer(ev,svg.node());const target=isDate?+x.invert(mx):x.invert(mx);
      const nx=all.reduce((a,b)=>Math.abs(b-target)<Math.abs(a-target)?b:a,all[0]);
      cross.attr('x1',x(isDate?new Date(nx):nx)).attr('x2',x(isDate?new Date(nx):nx)).attr('opacity',1);
      const rows=series.map(s=>{const p=s.pts.find(q=>+q.x===nx);return p?{color:s.color,text:`${s.name}: ${o.tipfmt(p.y)}`}:null;}).filter(Boolean);
      tip.show(x(isDate?new Date(nx):nx),y(ymax/2),o.titlefmt(nx,series),rows);})
    .on('pointerleave',()=>{cross.attr('opacity',0);tip.hide();});
}

/* ---------- vertical bars ---------- */
function vbars(box,rows,o){
  const H=o.height||220,left=o.left||46,right=10,top=14,bot=36;const {svg,W}=frame(box,H);
  const x=d3.scaleBand().domain(rows.map(r=>r.label)).range([left,W-right]).paddingInner(0.25),ymax=d3.max(rows,r=>r.value)||1,y=d3.scaleLinear().domain([0,ymax*1.12]).nice().range([H-bot,top]);
  yAxis(svg,y,W,left,right,o.yfmt,4);
  if(o.ref!==undefined){svg.append('line').attr('x1',left).attr('x2',W-right).attr('y1',y(o.ref)).attr('y2',y(o.ref)).attr('stroke',REF).attr('stroke-dasharray','4 4');}
  const tip=tipper(box);
  rows.forEach(r=>{const bx=x(r.label),bw=x.bandwidth();
    if(o.range&&r.lo!==undefined){svg.append('line').attr('x1',bx+bw/2).attr('x2',bx+bw/2).attr('y1',y(r.hi)).attr('y2',y(r.lo)).attr('stroke',AXIS).attr('stroke-width',1.5);}
    const h=Math.max(H-bot-y(r.value),0);
    const rect=svg.append('rect').attr('x',bx).attr('y',y(r.value)).attr('width',bw).attr('height',h).attr('rx',Math.min(4,bw/2)).attr('fill',r.color||C(0)).attr('opacity',r.partial?0.55:1);
    svg.append('text').attr('x',bx+bw/2).attr('y',H-bot+14).attr('text-anchor','middle').text(bw<26&&r.label.length>2&&!r.label.startsWith("'")?r.label.slice(0,1):r.label);
    if(o.valuelabels)svg.append('text').attr('x',bx+bw/2).attr('y',y(r.value)-4).attr('text-anchor','middle').text(o.vfmt(r.value));
    svg.append('rect').attr('x',bx-2).attr('y',top).attr('width',bw+4).attr('height',H-bot-top).attr('fill','transparent')
      .on('pointermove',(ev)=>{const [mx,my]=d3.pointer(ev,box);tip.show(mx,my,r.tip||r.label,[{color:r.color||C(0),text:o.tipfmt(r)}]);}).on('pointerleave',()=>tip.hide());
  });
  svg.append('line').attr('x1',left).attr('x2',W-right).attr('y1',H-bot).attr('y2',H-bot).attr('stroke',AXIS);
}

function fit(svg,str,maxW){if(textW(svg,str,11)<=maxW)return str;let t=str;while(t.length>3&&textW(svg,t+'…',11)>maxW)t=t.slice(0,-1);return t+'…';}
/* ---------- horizontal bars ---------- */
function hbars(box,rows,o){
  if(!rows.length){msg(box,'Nothing to show.');return;}
  const rowH=o.rowH||24,top=6,bot=24;const tmp=frame(box,40);const lw=Math.min(tmp.W*0.45,d3.max(rows,r=>textW(tmp.svg,r.label,11))+8);
  const H=top+bot+rows.length*rowH;const {svg,W}=frame(box,H);const left=Math.ceil(lw)+6,right=o.right||52;
  const x=d3.scaleLinear().domain([0,Math.max(d3.max(rows,r=>r.value)||1,o.min||0)*1.05]).range([left,W-right]);
  x.ticks(4).forEach(t=>{svg.append('line').attr('x1',x(t)).attr('x2',x(t)).attr('y1',top).attr('y2',H-bot).attr('stroke',GRID);svg.append('text').attr('x',x(t)).attr('y',H-8).attr('text-anchor','middle').text(o.xfmt(t));});
  if(o.ref!==undefined){svg.append('line').attr('x1',x(o.ref)).attr('x2',x(o.ref)).attr('y1',top).attr('y2',H-bot).attr('stroke',REF).attr('stroke-dasharray','4 4');}
  const tip=tipper(box);
  rows.forEach((r,i)=>{const y0=top+i*rowH,cy=y0+rowH/2;
    svg.append('text').attr('x',left-6).attr('y',cy+4).attr('text-anchor','end').text(fit(svg,r.label,left-12));
    if(o.range){svg.append('line').attr('x1',x(r.lo)).attr('x2',x(r.hi)).attr('y1',cy).attr('y2',cy).attr('stroke',AXIS).attr('stroke-width',2).attr('stroke-linecap','round');
      svg.append('circle').attr('cx',x(r.value)).attr('cy',cy).attr('r',5).attr('fill',r.color||C(0)).attr('stroke','var(--color-panel)').attr('stroke-width',1.5);}
    else svg.append('rect').attr('x',left).attr('y',cy-Math.min(10,rowH*0.34)).attr('width',Math.max(x(r.value)-left,1.5)).attr('height',Math.min(20,rowH*0.68)).attr('rx',4).attr('fill',r.color||C(0));
    svg.append('text').attr('x',(o.range?x(r.hi):x(r.value))+6).attr('y',cy+4).text(o.vfmt(r.value));
    svg.append('rect').attr('x',0).attr('y',y0).attr('width',W).attr('height',rowH).attr('fill','transparent')
      .on('pointermove',(ev)=>{const [mx,my]=d3.pointer(ev,box);tip.show(mx,my,r.label,[{color:r.color||C(0),text:o.tipfmt(r)}]);}).on('pointerleave',()=>tip.hide());});
}

/* ---------- table ---------- */
const FMT={share_pct:pct1,iqr_over_median_pct:pct0,change_pct:signed,median_ticket:n0,mean_ticket:n0,price_weighted:n0,price_plain_mean:n0};
const cellText=(f,v)=>v===null||v===undefined?'':(FMT[f]?FMT[f](v):(typeof v==='number'?n0(v):String(v)));
function fillTable(id,rows,keyFn){const tbl=$(id),tb=tbl.querySelector('tbody');tb.textContent='';const ths=[...tbl.querySelectorAll('th')];
  rows.forEach(r=>{const tr=document.createElement('tr');tr.dataset.key=keyFn(r);ths.forEach(th=>{const f=th.dataset.field,td=document.createElement('td');
    if(th.classList.contains('n'))td.className='n';else if(['finding','why','action'].includes(f))td.className='w';
    if(f==='severity'){const s=document.createElement('span');s.className='sev '+r[f];s.textContent=r[f];td.appendChild(s);}else td.textContent=cellText(f,r[f]);tr.appendChild(td);});tb.appendChild(tr);});}

/* ---------- segment helpers ---------- */
const bySeg=(rows)=>rows.filter(r=>r.payment===state.pay&&r.sale_type===state.st);
function segmentLabel(){return (state.pay==='All'?'all payment types':state.pay.toLowerCase())+', '+(state.st==='All'?'all sale types':state.st);}
function fillSelectors(){
  const y=get('yearly');if(!y)return;
  const pay=[...new Set(y.map(r=>r.payment))],st=[...new Set(y.map(r=>r.sale_type))];
  const order=(a)=>['All',...a.filter(v=>v!=='All').sort()];
  const sp=$('sel-pay'),ss=$('sel-st');
  if(!sp.options.length){order(pay).forEach(v=>sp.add(new Option(v==='All'?'All payment types':v,v)));order(st).forEach(v=>ss.add(new Option(v==='All'?'All sale types':v,v)));}
  sp.value=state.pay;ss.value=state.st;
  const sv=$('sel-vk');if(!sv.options.length){['State','Specialty'].forEach(v=>sv.add(new Option(v,v)));}sv.value=state.vk;
}

/* ---------- sections ---------- */
function drawHeader(){
  const k=get('kpis');const r=k&&k[0];
  const put=(el,f)=>{const v=r?r[f]:null;let t='—';
    if(v!==null&&v!==undefined){t=({last_12m_revenue:cmp.format(v),prior_12m_revenue:cmp.format(v),change_pct:signed(v),lines_change_pct:signed(v),last_12m_lines:n0(v),median_ticket:n0(v),mean_ticket:'mean '+n0(v),clients:n0(v),products:n0(v)})[f]??String(v);}
    el.textContent=t;
    if(f==='change_pct'||f==='lines_change_pct'){el.style.color=v<0?'var(--color-bad)':'var(--color-ok)';}};
  document.querySelectorAll('[data-source="kpis"]').forEach(el=>put(el,el.dataset.field));
}
function drawFindings(){
  const ins=get('insights');
  ['typical','variation','people'].forEach(t=>{const box=$('ins-'+t);box.textContent='';
    (ins||[]).filter(r=>r.tab===t).forEach(r=>{const c=document.createElement('div');c.className='card ins';
      const h=document.createElement('h3');h.textContent=r.title;const f=document.createElement('p');f.className='f';f.textContent=r.finding;
      const e=document.createElement('p');e.className='k';const eb=document.createElement('b');eb.textContent='Why it matters: ';e.append(eb,r.evidence);
      const a=document.createElement('p');a.className='k';const ab=document.createElement('b');ab.textContent='What to do: ';a.append(ab,r.action);
      const b=document.createElement('button');b.textContent='See the evidence';b.addEventListener('click',()=>show(t));
      c.append(h,f,e,a,b);box.appendChild(c);});});
  const hl=get('health');const line=$('health-line');
  if(hl){const hi=hl.filter(r=>r.severity==='High').length,me=hl.filter(r=>r.severity==='Medium').length;line.textContent=`${hl.length} things to know before trusting a number: ${hi} high, ${me} medium and ${hl.length-hi-me} low severity.`;}
}
function drawTypical(){
  const y=get('yearly'),box=$('ch-ticket');
  if(!y){return;}
  const rows=bySeg(y).sort((a,b)=>a.year-b.year);$('h-ticket').textContent='Median and mean sale line, by year ('+segmentLabel()+')';
  if(rows.length<2){['ch-ticket','ch-rev','ch-lines'].forEach(i=>msg($(i),'Fewer than two years of sales in this segment.'));$('lg-ticket').textContent='';}
  else{
    lineChart(box,[{name:'Median sale line',color:C(0),pts:rows.map(r=>({x:r.year,y:r.median_ticket,partial:r.partial}))},{name:'Mean sale line',color:C(1),pts:rows.map(r=>({x:r.year,y:r.mean_ticket,partial:r.partial}))}],
      {yfmt:(v)=>cmp.format(v),xfmt:(v)=>String(v),xticks:rows.map(r=>r.year),dots:true,tipfmt:(v)=>n0(v),titlefmt:(x)=>String(x)+(rows.find(r=>r.year===x&&r.partial)?' (partial year)':'')});
    legend('lg-ticket',[{name:'Median sale line',color:C(0)},{name:'Mean sale line',color:C(1)},{name:'Hollow dot, dashed line: partial year',color:'var(--cds-chart-muted,#9a9a95)',ring:true}]);
    vbars($('ch-rev'),rows.map(r=>({label:"'"+String(r.year).slice(2),value:r.revenue,partial:r.partial,tip:String(r.year)+(r.partial?' (partial)':''),color:C(0)})),{yfmt:(v)=>cmp.format(v),tipfmt:(r)=>'Revenue '+cmp.format(r.value),height:210});
    vbars($('ch-lines'),rows.map(r=>({label:"'"+String(r.year).slice(2),value:r.lines,partial:r.partial,tip:String(r.year)+(r.partial?' (partial)':''),color:C(2)})),{yfmt:(v)=>cmp.format(v),tipfmt:(r)=>n0(r.value)+' sale lines',height:210});
  }
  const cc=get('concentration');
  if(cc){const ents=['Products','Clients','Sale lines'];
    lineChart($('ch-conc'),ents.map((e,i)=>({name:e,color:C(i),pts:cc.filter(r=>r.entity===e).map(r=>({x:r.top_pct,y:r.cum_share_pct}))})),
      {yfmt:(v)=>v+'%',xfmt:(v)=>v+'%',left:44,tipfmt:(v)=>pct0(v)+' of revenue',titlefmt:(x)=>'Top '+x+'% of entities',height:250,refs:[{y:50,label:'half of revenue'}]});
    legend('lg-conc',ents.map((e,i)=>({name:e,color:C(i)})));}
  const pr=get('products');if(pr)fillTable('tb-products',pr,(r)=>String(r.rank));
}
function drawVariation(){
  const m=get('monthly');
  if(m){const rows=bySeg(m).sort((a,b)=>a.month<b.month?-1:1).filter(r=>r.month>='2019-01');
    if(rows.length<12)msg($('ch-month'),'Fewer than 12 months of sales in this segment since 2019.');
    else{const vals=rows.map(r=>r.revenue),med=d3.median(vals),spread=1.4826*d3.median(vals.map(v=>Math.abs(v-med)));
      lineChart($('ch-month'),[{name:'Monthly revenue',color:C(0),pts:rows.map(r=>({x:+new Date(r.month+'-01T00:00:00Z'),y:r.revenue}))}],
        {date:true,yfmt:(v)=>cmp.format(v),tipfmt:(v)=>cmp.format(v),titlefmt:(x)=>d3.utcFormat('%B %Y')(new Date(x)),height:260,left:54,refs:[{y:med,label:'median month'},{y:med+spread},{y:Math.max(med-spread,0)}]});
      legend('lg-month',[{name:'Monthly revenue ('+segmentLabel()+')',color:C(0)},{name:'Dashed: median month and ± one robust spread ('+cmp.format(spread)+')',color:'var(--cds-chart-reference)'}]);}}
  const b=get('bands');
  if(b){const W0=$('ch-bands');const H=250,left=46,right=10,top=14,bot=36;const {svg,W}=frame(W0,H);
    const x=d3.scaleBand().domain(b.map(r=>r.month)).range([left,W-right]).paddingInner(0.2);
    const lim=Math.max(45,d3.max(b,r=>Math.abs(r.deviation_pct))*1.1),y=d3.scaleLinear().domain([-lim,lim]).nice().range([H-bot,top]);
    svg.append('rect').attr('x',left).attr('width',W-left-right).attr('y',y(10)).attr('height',y(-10)-y(10)).attr('fill',MUTED).attr('opacity',0.18);
    yAxis(svg,y,W,left,right,(v)=>v+'%',5);svg.append('line').attr('x1',left).attr('x2',W-right).attr('y1',y(0)).attr('y2',y(0)).attr('stroke',AXIS);
    const tip=tipper(W0);
    b.forEach((r,i)=>{const bx=x(r.month),bw=x.bandwidth(),inside=Math.abs(r.deviation_pct)<=10,y0=y(Math.max(r.deviation_pct,0)),h=Math.abs(y(r.deviation_pct)-y(0));
      svg.append('rect').attr('x',bx).attr('y',y0).attr('width',bw).attr('height',Math.max(h,1)).attr('rx',Math.min(3,bw/2)).attr('fill',inside?MUTED:C(1));
      if(r.robust_flag==='unusual')svg.append('circle').attr('cx',bx+bw/2).attr('cy',r.deviation_pct>=0?y(r.deviation_pct)-8:y(r.deviation_pct)+8).attr('r',5).attr('fill','none').attr('stroke',C(0)).attr('stroke-width',2);
      if(i%Math.ceil(b.length/Math.max(3,Math.floor(W/70)))===0)svg.append('text').attr('x',bx+bw/2).attr('y',H-bot+14).attr('text-anchor','middle').text(d3.utcFormat('%b %y')(new Date(r.month+'-01T00:00:00Z')));
      svg.append('rect').attr('x',bx-1).attr('y',top).attr('width',bw+2).attr('height',H-bot-top).attr('fill','transparent').on('pointermove',(ev)=>{const [mx,my]=d3.pointer(ev,W0);
        tip.show(mx,my,d3.utcFormat('%B %Y')(new Date(r.month+'-01T00:00:00Z')),[{text:'Revenue '+cmp.format(r.revenue)},{text:signed(r.deviation_pct)+' vs 12-month average ('+r.fixed_band+')'},{text:r.robust_flag==='unusual'?'Unusual for its own history':'Normal for its own history'}]);}).on('pointerleave',()=>tip.hide());});
    legend('lg-bands',[{name:'Outside the fixed ±10% band',color:C(1)},{name:'Inside it (shaded: NEUTRAL band)',color:MUTED},{name:'Unusual for its own history',color:C(0),ring:true}]);
    const out=b.filter(r=>Math.abs(r.deviation_pct)>10).length,un=b.filter(r=>r.robust_flag==='unusual').length;
    $('nt-bands').textContent=`${out} of ${b.length} months fall outside the fixed ±10% band; ${un} are unusual against the history's own spread (about ±${d3.median(b,r=>r.normal_swing_pct).toFixed(0)}% in a typical month).`;}
  const v=get('volatility');
  if(v){const rows=v.filter(r=>r.kind!=='All sales').sort((a,b)=>b.cv_pct-a.cv_pct).map(r=>({label:(r.kind==='Block'?r.group:r.group+' ('+r.kind.toLowerCase()+')'),value:r.cv_pct,color:r.kind==='Block'?C(0):C(2),share:r.share_pct,max:r.max_over_median}));
    hbars($('ch-vol'),rows,{xfmt:(t)=>t+'%',vfmt:pct0,tipfmt:(r)=>pct0(r.value)+' variation; share of revenue '+pct1(r.share)+'; best month '+r.max.toFixed(1)+' × the median month',rowH:22});}
  const s=get('seasonality');
  if(s){vbars($('ch-seas'),s.map(r=>({label:MONTHS[r.calendar_month].slice(0,3),value:100*r.typical_index,lo:100*r.lowest_index,hi:100*r.highest_index,color:100*r.typical_index>=100?C(0):MUTED,tip:MONTHS[r.calendar_month]})),
      {yfmt:(t)=>t+'%',range:true,ref:100,tipfmt:(r)=>pct0(r.value)+' of trend (range '+pct0(r.lo)+' to '+pct0(r.hi)+')',height:250,valuelabels:false});}
}
function drawPeople(){
  const vb=get('visit_buckets');
  if(vb)hbars($('ch-vb'),vb.sort((a,b)=>a.order-b.order).map(r=>({label:r.bucket,value:r.share_pct,count:r.doctors,color:r.order>=2&&r.order<=4?C(1):(r.order===5?MUTED:C(0))})),{xfmt:(t)=>t+'%',vfmt:pct1,tipfmt:(r)=>n0(r.count)+' doctors',rowH:30,right:60});
  const vg=get('visit_groups');
  if(vg){const rows=vg.filter(r=>r.kind===state.vk).sort((a,b)=>a.median_days-b.median_days).map(r=>({label:r.group,value:r.median_days,lo:r.q1,hi:r.q3,n:r.doctors,over:r.over_90_pct,color:r.median_days>90?C(1):C(0)}));
    hbars($('ch-vg'),rows,{range:true,xfmt:(t)=>t,vfmt:(v)=>n0(v),ref:90,tipfmt:(r)=>'median '+n0(r.value)+' days (middle half '+n0(r.lo)+' to '+n0(r.hi)+'); '+pct0(r.over)+' over 90 days; '+n0(r.n)+' doctors',rowH:22,right:44});}
  const ch=get('churn');
  if(ch){const rows=ch.filter(r=>r.kind!=='All').sort((a,b)=>b.churn_pct-a.churn_pct).map(r=>({label:r.group+' ('+r.kind.toLowerCase()+')',value:r.churn_pct,n:r.patients_lines,color:r.kind==='Payment type'?C(0):C(2)}));
    const all=ch.find(r=>r.kind==='All');
    hbars($('ch-churn'),rows,{xfmt:(t)=>t+'%',vfmt:pct1,tipfmt:(r)=>n0(r.n)+' patient lines',rowH:24,ref:all?all.churn_pct:undefined});}
}
function drawHealth(){
  const h=get('health');
  if(h){const rank={High:0,Medium:1,Low:2};fillTable('tb-health',[...h].sort((a,b)=>rank[a.severity]-rank[b.severity]),(r)=>encodeURIComponent(r.column)+','+encodeURIComponent(r.finding));}
  const e=get('empty_cells');
  if(e)hbars($('ch-empty'),e.map(r=>({label:r.table+'.'+r.column,value:r.empty_pct,type:r.stored_type,color:C(1)})),{xfmt:(t)=>t+'%',vfmt:pct0,tipfmt:(r)=>pct1(r.value)+' empty; stored as '+r.type,rowH:24,right:46});
}

/* ---------- tabs and wiring ---------- */
function drawVisible(){
  drawHeader();
  fillSelectors();
  drawFindings();
  ({typical:drawTypical,variation:drawVariation,people:drawPeople,health:drawHealth})[state.tab]?.();
}
function show(which){
  state.tab=which;
  TABS.forEach(t=>{$('page-'+t).hidden=t!==which;$('tab-'+t).setAttribute('aria-selected',String(t===which));});
  try{dash.setLink(which);}catch(e){}
  drawVisible();
  window.scrollTo&&window.scrollTo({top:0});
}
TABS.forEach(t=>$('tab-'+t).addEventListener('click',()=>show(t)));
$('to-health').addEventListener('click',()=>show('health'));
$('sel-pay').addEventListener('change',()=>{state.pay=$('sel-pay').value;drawVisible();});
$('sel-st').addEventListener('change',()=>{state.st=$('sel-st').value;drawVisible();});
$('sel-vk').addEventListener('change',()=>{state.vk=$('sel-vk').value;drawVisible();});
dash.onData(drawVisible);
const named=TABS.find(t=>location.hash==='#'+t);if(named)show(named);
})();
