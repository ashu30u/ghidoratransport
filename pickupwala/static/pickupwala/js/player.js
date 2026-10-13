(function(){
  var TRACKS = [];
  var SHAYARI = ["लोड हो रहा है…"];
  var CHAI_MESSAGES = [{ title: "Chai pe charcha! ☕", message: "Music baad mein, pehle chai!" }];
  var HORNS = [];
  var hornIdx = 0;
  var LIVE_RADIO_STREAMS = [
    { title: "Radio Mirchi 98.3 FM Live 📻", artist: "Mirchi Murga & Bollywood Hits", url: "http://peridot.streamguys.com:7150/Mirchi" },
    { title: "Mirchi Purani Jeans 98.3 FM 📻", artist: "Golden Retro Hits & RJ Naved", url: "https://node-19.zeno.fm/v34w8b6e618uv" },
    { title: "Radio City 91.1 FM Live 📻", artist: "Superhit Highway Radio", url: "http://prclive1.listenon.in:9960/" },
    { title: "Vividh Bharati 102.8 FM 📻", artist: "Akashvani National Live Stream", url: "https://air.radioca.st/stream" }
  ];
  var liveRadioIdx = 0;

  // Single background Audio object for preloading next track to eliminate startup delay
  var preloadAudio = new Audio();
  preloadAudio.preload = "auto";

  // Master State Object
  var state = {
    index: 0,
    playing: false,
    elapsed: 0,
    radioOn: false,
    teaActive: false,
    repeat: false,    // Repeat Mode: OFF by default
    autoNext: true,   // Auto Next Mode: ON by default
    timer: null,
    shayariIdx: 0,
    listeners: 537
  };

  var els = {
    listenerCount: document.getElementById('listenerCount'),
    clock: document.getElementById('clock'),
    signage: document.getElementById('signage'),
    signageText: document.getElementById('signageText'),
    trackTitle: document.getElementById('trackTitle'),
    trackArtist: document.getElementById('trackArtist'),
    cassette: document.getElementById('cassette'),
    cassetteArt: document.getElementById('cassetteArt'),
    roadFill: document.getElementById('roadFill'),
    progressTruck: document.getElementById('progressTruck'),
    roadProgress: document.querySelector('.road-progress'),
    roadTrack: document.querySelector('.road-track'),
    kmDone: document.getElementById('kmDone'),
    kmTotal: document.getElementById('kmTotal'),
    timeReadout: document.getElementById('timeReadout'),
    playBtn: document.getElementById('playBtn'),
    prevBtn: document.getElementById('prevBtn'),
    nextBtn: document.getElementById('nextBtn'),
    repeatBtn: document.getElementById('repeatBtn'),
    autoNextBtn: document.getElementById('autoNextBtn'),
    hornBtn: document.getElementById('hornBtn'),
    radioBtn: document.getElementById('radioBtn'),
    teaBtn: document.getElementById('teaBtn'),
    playlistBtn: document.getElementById('playlistBtn'),
    playlistSheet: document.getElementById('playlistSheet'),
    playlistList: document.getElementById('playlistList'),
    trackCount: document.getElementById('trackCount'),
    closePlaylist: document.getElementById('closePlaylist'),
    sheetBackdrop: document.getElementById('sheetBackdrop'),
    truckZone: document.getElementById('truckZone'),
    truckImg: document.getElementById('truckImg'),
    hornPopup: document.getElementById('hornPopup'),
    audioEl: document.getElementById('audioEl'),
    hornAudio: document.getElementById('hornAudio'),
    radioClickAudio: document.getElementById('radioClickAudio'),
    player: document.getElementById('player'),
    chaiPopup: document.getElementById('chaiPopup'),
    chaiTitle: document.getElementById('chaiTitle'),
    chaiSub: document.getElementById('chaiSub')
  };

  function fmtTime(sec){
    if (isNaN(sec) || !isFinite(sec) || sec < 0) return "0:00";
    sec = Math.floor(sec);
    var m = Math.floor(sec/60), s = sec%60;
    return m + ":" + (s<10?"0":"") + s;
  }

  function renderPlaylist(){
    if (!els.trackCount || !els.playlistList) return;
    els.trackCount.textContent = TRACKS.length + " Tracks";
    els.playlistList.innerHTML = "";
    if (!TRACKS.length){
      els.playlistList.innerHTML = '<li class="playlist-empty">Admin panel में अभी कोई song active नहीं है।</li>';
      return;
    }
    TRACKS.forEach(function(t, i){
      var li = document.createElement('li');
      li.className = 'track-row' + (i===state.index ? ' current' : '');
      var thumb = t.cover_url ? '<img src="'+t.cover_url+'" alt="">' : '🎵';
      li.innerHTML =
        '<span class="track-idx">'+(i+1)+'</span>' +
        '<span class="track-thumb">'+thumb+'</span>' +
        '<span class="track-meta"><span class="t-title">'+t.title+'</span><span class="t-artist">'+t.artist+'</span></span>' +
        '<span class="track-playing-icon">▶</span>';
      li.addEventListener('click', function(){
        resetChaiState();
        if (state.radioOn){
          state.radioOn = false;
          if (els.radioBtn) els.radioBtn.classList.remove('active');
          if (els.signage) els.signage.classList.remove('radio-on');
        }
        loadTrack(i, true);
        closeSheet();
      });
      els.playlistList.appendChild(li);
    });
  }

  // Preload next track in background to eliminate playback startup delay
  function preloadNextSong() {
    if (!TRACKS.length || TRACKS.length <= 1) return;
    var nextIdx = (state.index + 1) % TRACKS.length;
    var nextTrack = TRACKS[nextIdx];
    if (nextTrack && nextTrack.audio_url) {
      try {
        var nextUrl = new URL(nextTrack.audio_url, window.location.href).href;
        if (preloadAudio.src !== nextUrl) {
          preloadAudio.src = nextTrack.audio_url;
          preloadAudio.load();
        }
      } catch(e){}
    }
  }

  function loadTrack(i, autoPlay){
    if (!TRACKS.length) return;
    
    // Normalize song index
    state.index = (i + TRACKS.length) % TRACKS.length;
    state.elapsed = 0;
    pendingSeekTime = null;
    
    var t = TRACKS[state.index];
    if (els.trackTitle) els.trackTitle.textContent = t.title;
    if (els.trackArtist) els.trackArtist.textContent = t.artist;
    if (els.kmTotal) els.kmTotal.textContent = t.km || 0;
    if (els.kmDone) els.kmDone.textContent = 0;
    if (els.timeReadout) els.timeReadout.textContent = "0:00 / " + fmtTime(t.duration);

    // Immediately reset pickup position to 0% timeline start
    if (els.roadFill) els.roadFill.style.setProperty('width', '0%', 'important');
    if (els.progressTruck) els.progressTruck.style.setProperty('left', '0%', 'important');

    if (t.audio_url && els.audioEl){
      try {
        var cleanUrl = t.audio_url.replace(/%25/g, '%');
        var targetUrl = new URL(cleanUrl, window.location.href).href;
        if (els.audioEl.src !== targetUrl && els.audioEl.src !== cleanUrl) {
          els.audioEl.src = cleanUrl;
          els.audioEl.preload = "auto";
          els.audioEl.load();
        } else {
          els.audioEl.currentTime = 0;
        }
      } catch(e) {
        els.audioEl.src = t.audio_url;
      }
    }

    if (els.cassetteArt) {
      if (t.cover_url){
        els.cassetteArt.src = t.cover_url;
        els.cassetteArt.style.display = 'block';
      } else {
        els.cassetteArt.removeAttribute('src');
        els.cassetteArt.style.display = 'none';
      }
    }
    renderPlaylist();
    preloadNextSong();

    if (autoPlay) {
      play();
    } else {
      syncPickupToAudio(0);
    }
  }

  var isDraggingTruck = false;
  var pendingSeekTime = null;

  function getAudioDuration() {
    if (els.audioEl && els.audioEl.duration && !isNaN(els.audioEl.duration) && isFinite(els.audioEl.duration) && els.audioEl.duration > 0) {
      if (TRACKS.length && TRACKS[state.index]) {
        TRACKS[state.index].duration = els.audioEl.duration;
      }
      return els.audioEl.duration;
    }
    if (TRACKS.length && TRACKS[state.index] && TRACKS[state.index].duration && !isNaN(TRACKS[state.index].duration) && TRACKS[state.index].duration > 0) {
      return TRACKS[state.index].duration;
    }
    return 0;
  }

  function getAudioCurrentTime() {
    if (isDraggingTruck || pendingSeekTime !== null || (els.audioEl && els.audioEl.seeking)) {
      return pendingSeekTime !== null ? pendingSeekTime : (els.audioEl ? els.audioEl.currentTime : 0);
    }
    if (els.audioEl && !isNaN(els.audioEl.currentTime) && isFinite(els.audioEl.currentTime)) {
      return els.audioEl.currentTime;
    }
    return 0;
  }

  /**
   * Master Authoritative Pickup Synchronization Function
   * Position % = audio.currentTime / audio.duration
   * Direct mathematical derivation ensures 100% accurate sync on play, pause, seek, and song change.
   */
  function syncPickupToAudio(overrideTime) {
    if (state.radioOn || !TRACKS.length) return;
    
    var duration = getAudioDuration();
    var currentTime = (overrideTime !== undefined && overrideTime !== null) ? overrideTime : getAudioCurrentTime();
    
    var progress = 0;
    if (duration > 0) {
      progress = Math.max(0, Math.min(1, currentTime / duration));
    }
    var pctStr = (progress * 100) + "%";
    var t = TRACKS[state.index];

    // Synchronize pickup vehicle position and road fill line immediately
    if (els.roadFill) els.roadFill.style.setProperty('width', pctStr, 'important');
    if (els.progressTruck) els.progressTruck.style.setProperty('left', pctStr, 'important');
    if (els.kmDone && t && t.km) els.kmDone.textContent = Math.round(progress * t.km);
    if (els.timeReadout) els.timeReadout.textContent = fmtTime(currentTime) + " / " + fmtTime(duration);
  }

  function updateProgressUI(){
    if (isDraggingTruck) return;
    syncPickupToAudio();
  }

  var lastTouchSeekTime = 0;

  function seekByEvent(e) {
    if (state.radioOn || !TRACKS.length) return;

    var now = Date.now();
    // Prevent synthetic mobile click events from re-triggering seek after touch gestures
    if (e.type === 'click' && (now - lastTouchSeekTime) < 450) {
      return;
    }
    if (e.type === 'touchstart' || e.type === 'pointerdown' || e.type === 'touchmove') {
      lastTouchSeekTime = now;
    }
    
    // Always measure relative to the full-width road track container
    var trackEl = els.roadTrack || document.querySelector('.road-track');
    if (!trackEl) return;
    
    var rect = trackEl.getBoundingClientRect();
    if (!rect || rect.width <= 0) return;
    
    var clientX = null;
    if (e.clientX !== undefined && e.clientX !== null && e.clientX > 0) {
      clientX = e.clientX;
    } else if (e.touches && e.touches.length > 0 && e.touches[0].clientX > 0) {
      clientX = e.touches[0].clientX;
    } else if (e.changedTouches && e.changedTouches.length > 0 && e.changedTouches[0].clientX > 0) {
      clientX = e.changedTouches[0].clientX;
    }
    
    // CRITICAL SAFETY CHECK: Ignore invalid, 0, or negative clientX values (prevents resetting to 1st second)
    if (clientX === null || isNaN(clientX) || clientX <= 0) {
      return;
    }
    
    var offsetX = clientX - rect.left;
    var pct = Math.max(0, Math.min(1, offsetX / rect.width));
    var duration = getAudioDuration();
    if (duration <= 0) return;
    
    var targetTime = pct * duration;
    
    // Lock pendingSeekTime during seeking to eliminate temporary audio latency jumps
    pendingSeekTime = targetTime;
    
    // 0ms Visual updates for instant pickup feedback
    syncPickupToAudio(targetTime);

    // Synchronize HTML5 audio element current time
    if (els.audioEl && !isNaN(targetTime)) {
      try {
        var clampedTime = Math.max(0, Math.min(duration - 0.1, targetTime));
        els.audioEl.currentTime = clampedTime;
      } catch(err){
        console.warn("Audio currentTime set error:", err);
      }
    }
  }

  // Single Animation Frame Loop for 60fps smooth rendering
  function smoothProgressLoop(){
    if (!state.radioOn && state.playing && TRACKS.length && !isDraggingTruck) {
      syncPickupToAudio();
    }
    requestAnimationFrame(smoothProgressLoop);
  }
  requestAnimationFrame(smoothProgressLoop);

  function resetChaiState(){
    if (state.teaActive){
      state.teaActive = false;
      if (els.teaBtn) els.teaBtn.classList.remove('active');
      if (els.chaiPopup) els.chaiPopup.classList.remove('active');
    }
  }

  function play(){
    if (state.radioOn){
      playRadioStream(0);
      return;
    }
    if (!TRACKS.length) return;
    resetChaiState();
    state.playing = true;
    if (els.playBtn) {
      els.playBtn.textContent = "⏸";
      els.playBtn.classList.remove('buffering');
    }
    if (els.cassette) els.cassette.classList.add('spin');
    
    var p = els.audioEl.play();
    if (p !== undefined){
      p.catch(function(err){
        console.warn("Audio playback buffering or blocked:", err);
        if (state.playing) {
          if (els.playBtn) els.playBtn.classList.add('buffering');
          var onCanPlay = function() {
            els.audioEl.removeEventListener('canplay', onCanPlay);
            if (state.playing) {
              els.audioEl.play().catch(function(e) {
                console.warn("Auto-play on canplay failed:", e);
              });
            }
          };
          els.audioEl.addEventListener('canplay', onCanPlay);
        }
      });
    }
  }

  function pause(){
    state.playing = false;
    if (els.playBtn) els.playBtn.textContent = "▶";
    if (els.cassette) els.cassette.classList.remove('spin');
    if (els.audioEl) els.audioEl.pause();
    syncPickupToAudio();
  }

  function togglePlay(){ state.playing ? pause() : play(); }

  // Toggle Repeat Mode
  function toggleRepeat(){
    state.repeat = !state.repeat;
    if (els.repeatBtn) {
      els.repeatBtn.classList.toggle('active', state.repeat);
      els.repeatBtn.title = state.repeat ? "Repeat (ON)" : "Repeat (OFF)";
    }
  }

  // Toggle Auto Next Mode
  function toggleAutoNext(){
    state.autoNext = !state.autoNext;
    if (els.autoNextBtn) {
      els.autoNextBtn.classList.toggle('active', state.autoNext);
      els.autoNextBtn.title = state.autoNext ? "Auto Next (ON)" : "Auto Next (OFF)";
    }
  }

  function nextTrack(){
    resetChaiState();
    if (state.radioOn){
      try {
        els.radioClickAudio.currentTime = 0;
        els.radioClickAudio.play().catch(function(){});
      } catch(e){}
      liveRadioIdx++;
      playRadioStream(0);
      return;
    }
    loadTrack(state.index + 1, true);
  }

  function prevTrack(){
    resetChaiState();
    if (state.radioOn){
      try {
        els.radioClickAudio.currentTime = 0;
        els.radioClickAudio.play().catch(function(){});
      } catch(e){}
      liveRadioIdx = (liveRadioIdx - 1 + LIVE_RADIO_STREAMS.length) % LIVE_RADIO_STREAMS.length;
      playRadioStream(0);
      return;
    }
    loadTrack(state.index - 1, true);
  }

  // Web Audio API Pressure Horn Synthesizer (100% reliable fallback sound generator)
  function playSynthesizedHorn() {
    try {
      var AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      var ctx = new AudioContext();
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      
      var osc1 = ctx.createOscillator();
      var osc2 = ctx.createOscillator();
      var gain = ctx.createGain();

      osc1.type = 'sawtooth';
      osc2.type = 'square';

      osc1.frequency.setValueAtTime(375, ctx.currentTime);
      osc2.frequency.setValueAtTime(455, ctx.currentTime);

      osc1.frequency.exponentialRampToValueAtTime(350, ctx.currentTime + 0.35);
      osc2.frequency.exponentialRampToValueAtTime(430, ctx.currentTime + 0.35);

      gain.gain.setValueAtTime(0.35, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.38);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(ctx.currentTime);
      osc2.start(ctx.currentTime);
      osc1.stop(ctx.currentTime + 0.4);
      osc2.stop(ctx.currentTime + 0.4);
    } catch(e) {
      console.warn("WebAudio horn fallback error:", e);
    }
  }

  var hornPopTimeout = null;
  var HORN_TEXTS = ["PEEP PEEP! 🎺", "HORN OK PLEASE! 🚚💨", "BOP BOP! 🎺", "RASTA DO BHAI! 🚚✨", "PEEP PEEP! 😎"];
  var hornTextIdx = 0;

  function honk(){
    var soundPlayed = false;
    var hornTitleToShow = "";

    function fallbackSound() {
      if (soundPlayed) return;
      if (els.hornAudio) {
        try {
          els.hornAudio.currentTime = 0;
          var p = els.hornAudio.play();
          if (p !== undefined) {
            p.then(function(){ soundPlayed = true; }).catch(function(){
              try {
                var fallbackAudio = new Audio('/static/pickupwala/audio/horn.wav');
                fallbackAudio.play().then(function(){ soundPlayed = true; }).catch(function(){
                  playSynthesizedHorn();
                });
              } catch(err){
                playSynthesizedHorn();
              }
            });
          } else {
            soundPlayed = true;
          }
        } catch(e) {
          playSynthesizedHorn();
        }
      } else {
        playSynthesizedHorn();
      }
    }

    if (HORNS.length > 0) {
      var currentIdx = hornIdx % HORNS.length;
      var hItem = HORNS[currentIdx];
      hornIdx++;

      if (hItem && hItem.title) {
        hornTitleToShow = HORN_TEXTS[hornTextIdx % HORN_TEXTS.length];
        hornTextIdx++;
      }

      if (hItem && hItem.url) {
        try {
          var hAudio = hItem._audioObj ? hItem._audioObj.cloneNode(true) : new Audio(hItem.url);
          var p2 = hAudio.play();
          if (p2 !== undefined) {
            p2.then(function(){ soundPlayed = true; }).catch(function(err){
              console.warn("API horn sound failed, falling back...", err);
              fallbackSound();
            });
          } else {
            soundPlayed = true;
          }
        } catch(e) {
          fallbackSound();
        }
      } else {
        fallbackSound();
      }
    } else {
      fallbackSound();
    }

    // Visual Honk Effect on Truck Background Image
    var targetImg = els.truckImg || els.truckZone || document.querySelector('.bg-hero-img');
    if (targetImg) {
      targetImg.classList.remove('honk-effect');
      void targetImg.offsetWidth;
      targetImg.classList.add('honk-effect');
      setTimeout(function(){ targetImg.classList.remove('honk-effect'); }, 450);
    }

    // Visual Honk Effect on Horn Button
    if (els.hornBtn) {
      els.hornBtn.classList.remove('btn-honk-bounce');
      void els.hornBtn.offsetWidth;
      els.hornBtn.classList.add('btn-honk-bounce');
      setTimeout(function(){ els.hornBtn.classList.remove('btn-honk-bounce'); }, 450);
    }

    // Floating Horn Speech Bubble Toast
    if (els.hornPopup) {
      if (!hornTitleToShow) {
        hornTitleToShow = HORN_TEXTS[hornTextIdx % HORN_TEXTS.length];
        hornTextIdx++;
      }
      els.hornPopup.textContent = hornTitleToShow;
      els.hornPopup.classList.add('active');
      clearTimeout(hornPopTimeout);
      hornPopTimeout = setTimeout(function(){
        els.hornPopup.classList.remove('active');
      }, 1400);
    }
  }

  function toggleTea(){
    state.teaActive = !state.teaActive;
    if (state.teaActive){
      pause();
      if (els.teaBtn) els.teaBtn.classList.add('active');
      if (CHAI_MESSAGES.length && els.chaiTitle && els.chaiSub){
        var item = CHAI_MESSAGES[Math.floor(Math.random() * CHAI_MESSAGES.length)];
        els.chaiTitle.textContent = item.title || "Chai pe charcha! ☕";
        els.chaiSub.textContent = item.message || "Music baad mein, pehle chai!";
      }
      if (els.chaiPopup) els.chaiPopup.classList.add('active');
    } else {
      if (els.teaBtn) els.teaBtn.classList.remove('active');
      if (els.chaiPopup) els.chaiPopup.classList.remove('active');
      play();
    }
  }

  var shayariTimer = null;
  function showShayari(i){
    if (!SHAYARI.length || !els.signage || !els.signageText) return;
    els.signage.classList.add('fade');
    setTimeout(function(){
      els.signageText.textContent = SHAYARI[i % SHAYARI.length];
      els.signage.classList.remove('fade');
    }, 220);
  }
  function startShayariCycle(interval){
    clearInterval(shayariTimer);
    shayariTimer = setInterval(function(){
      state.shayariIdx = (state.shayariIdx + 1) % SHAYARI.length;
      showShayari(state.shayariIdx);
    }, interval);
  }

  function playRadioStream(retryOffset){
    retryOffset = retryOffset || 0;
    var stations = LIVE_RADIO_STREAMS.slice();
    if (TRACKS.length > 0) {
      TRACKS.forEach(function(tr){
        if (tr.audio_url) {
          stations.push({
            title: tr.title + " (Mirchi Live 98.3 📻)",
            artist: tr.artist + " — Radio Mirchi Stream",
            url: tr.audio_url
          });
        }
      });
    }

    if (retryOffset >= stations.length){
      if (TRACKS.length && TRACKS[state.index] && TRACKS[state.index].audio_url) {
        if (els.trackTitle) els.trackTitle.textContent = "Radio Mirchi 98.3 FM Live 📻";
        if (els.trackArtist) els.trackArtist.textContent = "Mirchi Murga & RJ Naved Comedy";
        els.audioEl.src = TRACKS[state.index].audio_url;
        try { els.audioEl.load(); } catch(e){}
        els.audioEl.play().catch(function(){});
      }
      return;
    }
    
    var idx = (liveRadioIdx + retryOffset) % stations.length;
    var radioStation = stations[idx];

    state.playing = true;
    if (els.playBtn) els.playBtn.textContent = "⏸";
    if (els.cassette) els.cassette.classList.add('spin');
    if (els.trackTitle) els.trackTitle.textContent = radioStation.title;
    if (els.trackArtist) els.trackArtist.textContent = radioStation.artist;
    if (els.kmTotal) els.kmTotal.textContent = "LIVE";
    if (els.kmDone) els.kmDone.textContent = "LIVE";
    if (els.timeReadout) els.timeReadout.textContent = "RADIO MIRCHI 98.3 LIVE 📻";
    if (els.roadFill) els.roadFill.style.width = "100%";
    if (els.progressTruck) els.progressTruck.style.left = "100%";

    els.audioEl.src = radioStation.url;
    try { els.audioEl.load(); } catch(e){}
    
    var p = els.audioEl.play();
    if (p !== undefined){
      p.catch(function(err){
        console.warn("Mirchi Live stream failed, auto switching...", err);
        playRadioStream(retryOffset + 1);
      });
    }
  }

  function toggleRadio(){
    resetChaiState();
    state.radioOn = !state.radioOn;
    if (els.radioBtn) els.radioBtn.classList.toggle('active', state.radioOn);
    if (els.signage) els.signage.classList.toggle('radio-on', state.radioOn);

    try {
      els.radioClickAudio.currentTime = 0;
      els.radioClickAudio.play().catch(function(){});
    } catch(e){}

    if (state.radioOn){
      playRadioStream(0);
      startShayariCycle(2600);
    } else {
      startShayariCycle(5200);
      if (TRACKS.length){
        loadTrack(state.index, true);
      } else {
        pause();
      }
    }
  }

  function openSheet(){
    if (els.playlistSheet) els.playlistSheet.classList.add('open');
    if (els.sheetBackdrop) els.sheetBackdrop.classList.add('open');
  }
  function closeSheet(){
    if (els.playlistSheet) els.playlistSheet.classList.remove('open');
    if (els.sheetBackdrop) els.sheetBackdrop.classList.remove('open');
  }

  function updateClock(){
    if (!els.clock) return;
    var d = new Date();
    var h = d.getHours(), m = d.getMinutes(), s = d.getSeconds();
    var ampm = h >= 12 ? "pm" : "am";
    var h12 = h % 12; if (h12 === 0) h12 = 12;
    var mStr = m < 10 ? "0" + m : m;
    var sStr = s < 10 ? "0" + s : s;
    els.clock.innerHTML = h12 + ":" + mStr + ":" + sStr + '<span class="ampm">' + ampm + '</span>';
  }

  function driftListeners(){
    if (!els.listenerCount) return;
    var delta = Math.round((Math.random()-0.55) * 14);
    state.listeners = Math.max(410, Math.min(920, state.listeners + delta));
    els.listenerCount.textContent = state.listeners;
  }

  // HTML5 Audio Event Listeners (Attached ONCE for strict synchronization)
  els.audioEl.addEventListener('timeupdate', function(){
    if (!isDraggingTruck) {
      if (pendingSeekTime !== null && els.audioEl.currentTime && Math.abs(els.audioEl.currentTime - pendingSeekTime) < 0.5) {
        pendingSeekTime = null;
      }
      syncPickupToAudio();
    }
  });

  els.audioEl.addEventListener('seeked', function(){
    setTimeout(function(){
      pendingSeekTime = null;
      syncPickupToAudio();
    }, 50);
  });

  els.audioEl.addEventListener('loadedmetadata', function(){
    if (els.audioEl && els.audioEl.duration && TRACKS.length && TRACKS[state.index]) {
      TRACKS[state.index].duration = els.audioEl.duration;
    }
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('canplay', function(){
    if (els.playBtn) els.playBtn.classList.remove('buffering');
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('waiting', function(){
    if (state.playing && els.playBtn) {
      els.playBtn.classList.add('buffering');
    }
  });

  els.audioEl.addEventListener('durationchange', function(){
    if (els.audioEl && els.audioEl.duration && TRACKS.length && TRACKS[state.index]) {
      TRACKS[state.index].duration = els.audioEl.duration;
    }
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('play', function(){
    state.playing = true;
    if (els.playBtn) els.playBtn.textContent = "⏸";
    if (els.cassette) els.cassette.classList.add('spin');
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('playing', function(){
    state.playing = true;
    if (els.playBtn) {
      els.playBtn.textContent = "⏸";
      els.playBtn.classList.remove('buffering');
    }
    if (els.cassette) els.cassette.classList.add('spin');
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('pause', function(){
    state.playing = false;
    if (els.playBtn) {
      els.playBtn.textContent = "▶";
      els.playBtn.classList.remove('buffering');
    }
    if (els.cassette) els.cassette.classList.remove('spin');
    syncPickupToAudio();
  });

  els.audioEl.addEventListener('error', function(err){
    console.warn("Audio element error on track:", TRACKS[state.index], err);
    if (!state.radioOn && TRACKS.length > 1) {
      if (TRACKS[state.index]) TRACKS[state.index]._errorCount = (TRACKS[state.index]._errorCount || 0) + 1;
      if (TRACKS[state.index]._errorCount <= 2) {
        setTimeout(function(){
          console.log("Auto-skipping unplayable track to next song...");
          nextTrack();
        }, 200);
        return;
      }
    }
    if (TRACKS[state.index] && !TRACKS[state.index]._fallbackTried) {
      TRACKS[state.index]._fallbackTried = true;
      els.audioEl.src = "https://stream.zeno.fm/f3wvbb142p8uv";
      try { els.audioEl.load(); els.audioEl.play(); } catch(e){}
    }
  });

  /**
   * REQUIREMENT 9: Repeat & Auto Next Priority Logic
   * Priority:
   * 1. If Repeat is ON: current song ends -> replay current song from 0:00
   * 2. If Repeat is OFF and Auto Next is ON: current song ends -> play next song
   * 3. If both are OFF: current song ends -> stop playback and reset position to 0:00
   */
  els.audioEl.addEventListener('ended', function(){
    if (state.radioOn) return;

    if (state.repeat) {
      // Repeat is ON: replay same song from beginning
      els.audioEl.currentTime = 0;
      syncPickupToAudio(0);
      var p = els.audioEl.play();
      if (p !== undefined) {
        p.catch(function(err) { console.warn("Repeat playback error:", err); });
      }
    } else if (state.autoNext) {
      // Repeat is OFF, Auto Next is ON: play next song in playlist
      nextTrack();
    } else {
      // Both OFF: stop playback and reset pickup to 0:00
      pause();
      els.audioEl.currentTime = 0;
      syncPickupToAudio(0);
    }
  });

  // Attach Control Button Handlers
  if (els.playBtn) els.playBtn.addEventListener('click', togglePlay);
  if (els.nextBtn) els.nextBtn.addEventListener('click', nextTrack);
  if (els.prevBtn) els.prevBtn.addEventListener('click', prevTrack);
  if (els.repeatBtn) els.repeatBtn.addEventListener('click', toggleRepeat);
  if (els.autoNextBtn) els.autoNextBtn.addEventListener('click', toggleAutoNext);
  if (els.hornBtn) els.hornBtn.addEventListener('click', honk);
  if (els.radioBtn) els.radioBtn.addEventListener('click', toggleRadio);
  if (els.teaBtn) els.teaBtn.addEventListener('click', toggleTea);
  if (els.playlistBtn) els.playlistBtn.addEventListener('click', openSheet);
  if (els.closePlaylist) els.closePlaylist.addEventListener('click', closeSheet);
  if (els.sheetBackdrop) els.sheetBackdrop.addEventListener('click', closeSheet);

  // Interactive Drag & Seek on Pickup / Road Progress Bar
  function handleSeekClick(e) {
    if (state.radioOn || !TRACKS.length) return;
    seekByEvent(e);
  }

  function startDrag(e) {
    if (state.radioOn || !TRACKS.length) return;
    isDraggingTruck = true;
    if (els.roadProgress) els.roadProgress.classList.add('dragging');
    if (els.progressTruck) els.progressTruck.classList.add('dragging');

    if (e && e.target && typeof e.target.setPointerCapture === 'function' && e.pointerId !== undefined) {
      try { e.target.setPointerCapture(e.pointerId); } catch(err){}
    }
    
    if (e && e.preventDefault && e.type !== 'touchstart' && e.type !== 'touchmove') {
      e.preventDefault();
    }
    seekByEvent(e);
  }

  function moveDrag(e) {
    if (!isDraggingTruck) return;
    if (e && e.preventDefault && e.type !== 'touchmove') {
      e.preventDefault();
    }
    seekByEvent(e);
  }

  function stopDrag(e) {
    if (!isDraggingTruck) return;
    isDraggingTruck = false;
    if (els.roadProgress) els.roadProgress.classList.remove('dragging');
    if (els.progressTruck) els.progressTruck.classList.remove('dragging');

    if (e && e.target && typeof e.target.releasePointerCapture === 'function' && e.pointerId !== undefined) {
      try { e.target.releasePointerCapture(e.pointerId); } catch(err){}
    }
    if (pendingSeekTime !== null) {
      syncPickupToAudio(pendingSeekTime);
      setTimeout(function(){ pendingSeekTime = null; }, 300);
    } else {
      syncPickupToAudio();
    }
  }

  [els.roadProgress, els.roadTrack, els.progressTruck, els.roadFill].forEach(function(elem) {
    if (!elem) return;
    elem.addEventListener('click', handleSeekClick);
    elem.addEventListener('pointerdown', startDrag);
    elem.addEventListener('mousedown', startDrag);
    elem.addEventListener('touchstart', startDrag, { passive: false });
  });

  window.addEventListener('pointermove', moveDrag);
  window.addEventListener('mousemove', moveDrag);
  window.addEventListener('touchmove', function(e) {
    if (isDraggingTruck) moveDrag(e);
  }, { passive: false });

  window.addEventListener('pointerup', stopDrag);
  window.addEventListener('pointercancel', stopDrag);
  window.addEventListener('mouseup', stopDrag);
  window.addEventListener('touchend', stopDrag);
  window.addEventListener('touchcancel', stopDrag);

  updateClock();
  setInterval(updateClock, 1000);
  setInterval(driftListeners, 3200);

  // Set initial button states
  if (els.repeatBtn) {
    els.repeatBtn.classList.toggle('active', state.repeat);
    els.repeatBtn.title = state.repeat ? "Repeat (ON)" : "Repeat (OFF)";
  }
  if (els.autoNextBtn) {
    els.autoNextBtn.classList.toggle('active', state.autoNext);
    els.autoNextBtn.title = state.autoNext ? "Auto Next (ON)" : "Auto Next (OFF)";
  }

  // Fetch playlist API
  fetch(window.PICKUPWALA_API)
    .then(function(r){ return r.json(); })
    .then(function(data){
      TRACKS = data.tracks || [];
      if (data.shayari && data.shayari.length) SHAYARI = data.shayari;
      if (data.chai && data.chai.length) CHAI_MESSAGES = data.chai;
      if (data.horns && data.horns.length) {
        HORNS = data.horns;
        HORNS.forEach(function(h) {
          try {
            var audioObj = new Audio();
            audioObj.src = h.url;
            audioObj.preload = "auto";
            audioObj.load();
            h._audioObj = audioObj;
          } catch(e){}
        });
      }
      state.shayariIdx = 0;
      showShayari(0);
      startShayariCycle(5200);
      if (TRACKS.length){
        loadTrack(0, false);
        updateProgressUI();
      } else {
        if (els.trackTitle) els.trackTitle.textContent = "कोई song उपलब्ध नहीं";
        if (els.trackArtist) els.trackArtist.textContent = "Admin panel से song add करें";
        renderPlaylist();
      }
    })
    .catch(function(){
      if (els.trackTitle) els.trackTitle.textContent = "Playlist लोड नहीं हुई";
      if (els.trackArtist) els.trackArtist.textContent = "API check करें";
    });
})();
