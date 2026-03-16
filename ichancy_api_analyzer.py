# -*- coding: utf-8 -*-
"""
محلل كود Ichancy React API
"""

import re

def analyze_react_code(html_code):
    """تحليل كود React واستخلاص معلومات API"""
    
    # استخلاص chunks المهمة
    chunk_pattern = r'"(\d+)":"([a-f0-9]+)"'
    chunks = re.findall(chunk_pattern, html_code)
    
    print("🔍 تحليل كود React Ichancy:")
    print("=" * 50)
    
    # استخلاص مسارات JavaScript
    js_pattern = r'static/js/(\d+)\.([a-f0-9]+)\.chunk\.js'
    js_files = re.findall(js_pattern, html_code)
    
    print(f"📁 ملفات JavaScript المكتشفة ({len(js_files)}):")
    for chunk_id, hash_val in js_files[:10]:  # أول 10 ملفات
        print(f"   - Chunk {chunk_id}: {hash_val}")
    
    # استخلاص مسارات CSS
    css_pattern = r'static/css/(\d+)\.([a-f0-9]+)\.chunk\.css'
    css_files = re.findall(css_pattern, html_code)
    
    print(f"\n🎨 ملفات CSS المكتشفة ({len(css_files)}):")
    for chunk_id, hash_val in css_files[:5]:  # أول 5 ملفات
        print(f"   - Chunk {chunk_id}: {hash_val}")
    
    # البحث عن endpoints محتملة في الكود
    api_patterns = [
        r'/api/[^"\s]+',
        r'/global/api/[^"\s]+',
        r'/Agent/[^"\s]+',
        r'/Player/[^"\s]+',
        r'/Transaction/[^"\s]+'
    ]
    
    print(f"\n🔗 Endpoints المحتملة:")
    found_endpoints = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, html_code)
        for match in matches:
            found_endpoints.add(match)
    
    for endpoint in sorted(found_endpoints):
        print(f"   - {endpoint}")
    
    # استخلاص معلومات webpack
    webpack_pattern = r'webpackJsonpaffiliates-front-end'
    if webpack_pattern in html_code:
        print(f"\n📦 تم اكتشاف تطبيق React (Webpack Bundle)")
        print("   - اسم التطبيق: affiliates-front-end")
    
    # استخلاص مسارات القوالب
    template_pattern = r'/global/templates/template/build'
    if template_pattern in html_code:
        print(f"\n🏗️ مسار القوالب: {template_pattern}")
    
    return {
        'js_files': js_files,
        'css_files': css_files,
        'endpoints': list(found_endpoints),
        'template_path': '/global/templates/template/build'
    }

# الكود الذي قدمته
html_code = """<!doctype html><html lang="en"><head><meta charset="utf-8"/><link rel="shortcut icon" id="favicon" href="/global/templates/template/build/favicon.ico"/><meta name="viewport" content="initial-scale=1,width=device-width,maximum-scale=1,viewport-fit=cover"/><meta name="theme-color" content="#000000"/><meta name="description" content="Marketing program for the gaming industry"/><link rel="apple-touch-icon" href="/global/templates/template/build/logo/logo-152x152.png"/><link rel="apple-touch-icon" href="/global/templates/template/build/logo/logo-167x167.png"/><link rel="apple-touch-icon" href="/global/templates/template/build/logo/logo-180x180.png"/><link rel="manifest" href="/global/templates/template/build/manifest.json"/><link href="/global/templates/template/build/static/css/main.a00891ac.chunk.css" rel="stylesheet"></head><body><noscript>You need to enable JavaScript to run this app.</noscript><div id="root"></div><script>!function(e){function t(t){for(var a,c,n=t[0],o=t[1],b=t[2],u=0,l=[];u<n.length;u++)c=n[u],Object.prototype.hasOwnProperty.call(r,c)&&r[c]&&l.push(r[c][0]),r[c]=0;for(a in o)Object.prototype.hasOwnProperty.call(o,a)&&(e[a]=o[a]);for(i&&i(t);l.length;)l.shift()();return f.push.apply(f,b||[]),d()}function d(){for(var e,t=0;t<f.length;t++){for(var d=f[t],a=!0,c=1;c<d.length;c++){var o=d[c];0!==r[o]&&(a=!1)}a&&(f.splice(t--,1),e=n(n.s=d[0]))}return e}var a={},c={6:0},r={6:0},f=[];function n(t){if(a[t])return a[t].exports;var d=a[t]={i:t,l:!1,exports:{}};return e[t].call(d.exports,d,d.exports,n),d.l=!0,d.exports}n.e=function(e){var t=[];c[e]?t.push(c[e]):0!==c[e]&&{0:1,2:1,4:1,9:1,10:1,11:1,12:1,13:1,14:1,15:1,16:1,17:1,18:1,19:1,20:1,21:1,23:1,24:1,25:1,26:1,27:1,28:1,29:1,30:1,31:1,32:1,33:1,34:1,35:1,36:1,37:1,38:1,39:1,40:1,41:1,42:1,43:1,44:1,45:1,46:1,47:1,48:1,49:1,50:1,51:1,65:1,66:1}[e]&&t.push(c[e]=new Promise((function(t,d){for(var a="static/css/"+({}[e]||e)+"."+{0:"a8bf5753",1:"31d6cfe0",2:"1d28c9cd",3:"31d6cfe0",4:"1f90a0bc",8:"31d6cfe0",9:"942a20b6",10:"a4ca29cd",11:"0d8d3ae7",12:"237ac7bc",13:"269dffc2",14:"fbfb9a59",15:"65cfb083",16:"9950139e",17:"033882ed",18:"26a303b6",19:"e41d957c",20:"c360b2c2",21:"9bb9c1f9",22:"31d6cfe0",23:"eacbc486",24:"21e59ae9",25:"21e59ae9",26:"27c6eeb2",27:"4028ee04",28:"bfda965f",29:"9ce11775",30:"2814d087",31:"281d087",32:"55ea7dd7",33:"f3c51d61",34:"92563fd7",35:"74746a4b",36:"edfd3d7e",37:"a46e6355",38:"9857a5aa",39:"95d18b3b",40:"15d9d4f4",41:"15d9d4f4",42:"15d9d4f4",43:"15d9d4f4",44:"95f02047",45:"3a0b274b",46:"70e20765",47:"5d7d2871",48:"f8913cb3",49:"3fc6fc09",50:"45a8bfed",51:"a8bbb428",52:"31d6cfe0",53:"31d6cfe0",54:"31d6cfe0",55:"31d6cfe0",56:"31d6cfe0",57:"31d6cfe0",58:"31d6cfe0",59:"31d6cfe0",60:"31d6cfe0",61:"31d6cfe0",62:"31d6cfe0",63:"31d6cfe0",64:"31d6cfe0",65:"c8f0e0ee",66:"a95371fe",67:"31d6cfe0",68:"31d6cfe0",69:"31d6cfe0",70:"31d6cfe0",71:"31d6cfe0",72:"31d6cfe0",73:"31d6cfe0",74:"31d6cfe0",75:"31d6cfe0",76:"31d6cfe0",77:"31d6cfe0",78:"31d6cfe0",79:"31d6cfe0"}[e]+".chunk.css",r=n.p+a,f=document.getElementsByTagName("link"),o=0;o<f.length;o++){var b=(i=f[o]).getAttribute("data-href")||i.getAttribute("href");if("stylesheet"===i.rel&&(b===a||b===r))return t()}var u=document.getElementsByTagName("style");for(o=0;o<u.length;o++){var i;if((b=(i=u[o]).getAttribute("data-href"))===a||b===r)return t()}var l=document.createElement("link");l.rel="stylesheet",l.type="text/css",l.onload=t,l.onerror=function(t){var a=t&&t.target&&t.target.src||r,f=new Error("Loading CSS chunk "+e+" failed.\n("+a+")");f.code="CSS_CHUNK_LOAD_FAILED",f.request=a,delete c[e],l.parentNode.removeChild(l),d(f)},l.href=r,document.getElementsByTagName("head")[0].appendChild(l)})).then((function(){c[e]=0})));var d=r[e];if(0!==d)if(d)t.push(d[2]);else{var a=new Promise((function(t,a){d=r[e]=[t,a]});t.push(d[2]=a);var f,o=document.createElement("script");o.charset="utf-8",o.timeout=120,n.nc&&o.setAttribute("nonce",n.nc),o.src=function(e){return n.p+"static/js/"+({}[e]||e)+"."+{0:"6cf10663",1:"1445c717",2:"c2ccd72b",3:"9ed3ca55",4:"9b190817",8:"f9abd9f9",9:"8f6bf836",10:"91cd58fe",11:"df398651",12:"cb500ef9",13:"72110a5a",14:"cf0f4039",15:"4ad5e748",16:"d5f8d724",17:"2cd755f3",18:"7086b4a0",19:"454387c8",20:"73a917ec",21:"ce5ad181",22:"b40e797f",23:"0a1d9b27",24:"393d9ead",25:"e17d54a7",26:"4b232788",27:"9d015cf9",28:"33b55887",29:"dad0033e",30:"6e8e005d",31:"5c82c06a",32:"5d4948aa",33:"30ba5ca7",34:"46fb1707",35:"6b92b1a0",36:"5b0cc4d9",37:"ba4dddb3",38:"46a3c6ac",39:"27e3f8dd",40:"d2d8a60e",41:"f3f30fa2",42:"b721e037",43:"38338bb3",44:"a3d34dbf",45:"d6df1ea4",46:"26ecca21",47:"3eb17e86",48:"388e27ed",49:"02a756d6",50:"c68cb3da",51:"1267ba73",52:"924dfdaf",53:"e35e1aac",54:"cd3bae25",55:"dffe4e51",56:"14513929",57:"fb385d68",58:"0596021b",59:"8546b630",60:"7274773d",61:"6ecad078",62:"0e7fab00",63:"05be226c",64:"e4067998",65:"02e5de44",66:"bb744969",67:"7437455d",68:"82852b70",69:"01c61a96",70:"d2885e29",71:"6ce9a0d9",72:"9241533b",73:"075431b4",74:"c6a0e5b8",75:"c38cfa6a",76:"fbd4798e",77:"0fdd1d2f",78:"da601c80",79:"5228619e"}[e]+".chunk.js"}(e);var b=new Error;f=function(t){o.onerror=o.onload=null,clearTimeout(u);var d=r[e];if(0!==d){if(d){var a=t&&("load"===t.type?"missing":t.type),c=t&&t.target&&t.target.src;b.message="Loading chunk "+e+" failed.\n("+a+": "+c+")",b.name="ChunkLoadError",b.type=a,b.request=c,d[1](b)}r[e]=void 0}};var u=setTimeout((function(){f({type:"timeout",target:o})}),12e4);o.onerror=o.onload=f,document.head.appendChild(o)}return Promise.all(t)},n.m=e,n.c=a,n.d=function(e,t,d){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:d})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var d=Object.create(null);if(n.r(d),Object.defineProperty(d,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var a in e)n.d(d,a,function(t){return e[t]}.bind(null,a));return d},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="/global/templates/template/build/",n.oe=function(e){throw console.error(e),e};var o=this["webpackJsonpaffiliates-front-end"]=this["webpackJsonpaffiliates-front-end"]||[],b=o.push.bind(o);o.push=t,o=o.slice();for(var u=0;u<o.length;u++)t(o[u]);var i=b;d()}([])</script><script src="/global/templates/template/build/static/js/7.585e803b.chunk.js"></script><script src="/global/templates/template/build/static/js/main.150ea109.chunk.js"></script></body></html>"""

if __name__ == "__main__":
    result = analyze_react_code(html_code)
    
    print("\n" + "=" * 50)
    print("💡 التوصيات:")
    print("1. محاولة تحميل ملفات JavaScript وفحصها")
    print("2. استخدام Chrome DevTools لمراقبة طلبات الشبكة")
    print("3. البحث عن endpoints في ملفات JS المضغوطة")
    print("4. إضافة تأخير أطول في Selenium لانتظار تحميل البيانات")
