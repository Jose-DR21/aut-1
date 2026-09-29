'use client';

import {useEffect,useRef,useState} from 'react';

export default function GalleryViewer({groups}){
  const all=groups.flatMap(group=>group.items);
  const [selected,setSelected]=useState(null);
  const [zoom,setZoom]=useState(null);
  const closeRef=useRef(null);
  const imageViewport=useRef(null);
  const previousFocus=useRef(null);
  const touchStart=useRef(null);
  const show=index=>setSelected((index+all.length)%all.length);
  const open=index=>{previousFocus.current=document.activeElement;setZoom(null);show(index);};
  const close=()=>{setSelected(null);previousFocus.current?.focus();};
  const zoomIn=()=>setZoom(value=>value===null?1:Math.min(3,value+0.25));
  const zoomOut=()=>setZoom(value=>value===null?null:value<=1?null:Math.max(1,value-0.25));

  useEffect(()=>{
    if(selected===null)return;
    const oldOverflow=document.body.style.overflow;
    document.body.style.overflow='hidden';
    closeRef.current?.focus();
    if(imageViewport.current)imageViewport.current.scrollTop=0;
    const onKey=event=>{
      if(event.key==='Escape')close();
      if(event.key==='ArrowRight'){event.preventDefault();setSelected(index=>(index+1)%all.length);}
      if(event.key==='ArrowLeft'){event.preventDefault();setSelected(index=>(index-1+all.length)%all.length);}
      if(event.key==='+'||event.key==='='){event.preventDefault();zoomIn();}
      if(event.key==='-'){event.preventDefault();zoomOut();}
    };
    window.addEventListener('keydown',onKey);
    return ()=>{document.body.style.overflow=oldOverflow;window.removeEventListener('keydown',onKey);};
  },[selected,all.length]);

  let offset=0;
  return <>{groups.map(group=>{
    const start=offset;
    offset+=group.items.length;
    return <section className="gallery-section" key={group.title}><h2>{group.title} <span>({group.items.length})</span></h2><p>{group.description}</p><div className="gallery-grid">{group.items.map((item,index)=><button type="button" className="gallery-card" key={item.file} onClick={()=>open(start+index)} aria-label={`Ver ${item.label} en el visor`}><img src={item.url} alt="" loading="lazy"/><strong>{item.label}</strong><small>Ver en el visor ↗</small></button>)}</div></section>;
  })}{selected!==null&&<div className="gallery-overlay" role="presentation" onMouseDown={event=>{if(event.target===event.currentTarget)close();}}><div className="gallery-viewer" role="dialog" aria-modal="true" aria-label={`Visor de capturas: ${all[selected].label}`}><div className="gallery-viewer-bar"><div className="gallery-viewer-title"><span>{all[selected].group} · {selected+1} de {all.length}</span><strong>{all[selected].label}</strong></div><div className="gallery-viewer-actions"><button type="button" className="gallery-viewer-zoom" onClick={zoomOut} disabled={zoom===null} aria-label="Reducir zoom">−</button><span className="gallery-viewer-zoom-level">{zoom===null?'Ajustada':`${Math.round(zoom*100)} %`}</span><button type="button" className="gallery-viewer-zoom" onClick={zoomIn} disabled={zoom===3} aria-label="Ampliar zoom">+</button><button type="button" className="gallery-viewer-fit" onClick={()=>{setZoom(value=>value===null?1:null);if(imageViewport.current){imageViewport.current.scrollTop=0;imageViewport.current.scrollLeft=0;}}}>{zoom===null?'Ver a ancho':'Ajustar a pantalla'}</button><button type="button" className="gallery-viewer-close" ref={closeRef} onClick={close} aria-label="Cerrar visor">✕</button></div></div><div className="gallery-viewer-stage" onTouchStart={event=>{touchStart.current={x:event.touches[0]?.clientX,y:event.touches[0]?.clientY};}} onTouchEnd={event=>{if(!touchStart.current)return;const dx=event.changedTouches[0]?.clientX-touchStart.current.x;const dy=event.changedTouches[0]?.clientY-touchStart.current.y;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))show(selected+(dx<0?1:-1));touchStart.current=null;}}><button type="button" className="gallery-viewer-arrow" onClick={()=>show(selected-1)} aria-label="Captura anterior">←</button><div ref={imageViewport} className={`gallery-viewer-image-area${zoom!==null?' is-width':''}`}><img src={all[selected].url} alt={all[selected].label} style={zoom!==null?{width:`${zoom*100}%`}:undefined}/></div><button type="button" className="gallery-viewer-arrow" onClick={()=>show(selected+1)} aria-label="Captura siguiente">→</button></div><div className="gallery-viewer-help">{zoom!==null?'Desplázate dentro de la imagen · ':''}Usa ← → para cambiar de imagen · + − para zoom · Esc para cerrar</div></div></div>}</>;
}
