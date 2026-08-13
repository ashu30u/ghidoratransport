(function(){
  var TRACKS = [];
  var SHAYARI = ["लोड हो रहा है…"];
  var CHAI_MESSAGES = [{ title: "Chai pe charcha! ☕", message: "Music baad mein, pehle chai!" }];
  var LIVE_RADIO_STREAMS = [
    { title: "Radio Mirchi 98.3 FM Live 📻", artist: "Mirchi Murga & Bollywood Hits", url: "http://peridot.streamguys.com:7150/Mirchi" },
    { title: "Mirchi Purani Jeans 98.3 FM 📻", artist: "Golden Retro Hits & RJ Naved", url: "https://node-19.zeno.fm/v34w8b6e618uv" },
    { title: "Radio City 91.1 FM Live 📻", artist: "Superhit Highway Radio", url: "http://prclive1.listenon.in:9960/" },
    { title: "Vividh Bharati 102.8 FM 📻", artist: "Akashvani National Live Stream", url: "https://air.radioca.st/stream" }
  ];
  var liveRadioIdx = 0;
  var state = { index:0, playing:false, elapsed:0, radioOn:false, teaActive:false, timer:null, shayariIdx:0, listeners:537 };

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
    kmDone: document.getElementById('kmDone'),
    kmTotal: document.getElementById('kmTotal'),
    timeReadout: document.getElementById('timeReadout'),
    playBtn: document.getElementById('playBtn'),
    prevBtn: document.getElementById('prevBtn'),
    nextBtn: document.getElementById('nextBtn'),
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
    audioEl: document.getElementById('audioEl'),
    hornAudio: document.getElementById('hornAudio'),
    radioClickAudio: document.getElementById('radioClickAudio'),
    player: document.getElementById('player'),
    chaiPopup: document.getElementById('chaiPopup'),
    chaiTitle: document.getElementById('chaiTitle'),
    chaiSub: document.getElementById('chaiSub')
  };

  function fmtTime(sec){
    if (isNaN(sec) || !isFinite(sec)) return "0:00";
    sec = Math.max(0, Math.floor(sec));
    var m = Math.floor(sec/60), s = sec%60;
    return m + ":" + (s<10?"0":"") + s;
  }

  function renderPlaylist(){
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
          els.radioBtn.classList.remove('active');
          els.signage.classList.remove('radio-on');
        }
        loadTrack(i);
        play();
        closeSheet();
      });
      els.playlistList.appendChild(li);
    });
  }

  function loadTrack(i){
    if (!TRACKS.length) return;
    state.index = (i + TRACKS.length) % TRACKS.length;
    state.elapsed = 0;
    var t = TRACKS[state.index];
    els.trackTitle.textContent = t.title;
    els.trackArtist.textContent = t.artist;
    els.kmTotal.textContent = t.km;
    els.kmDone.textContent = 0;
    els.timeReadout.textContent = "0:00 / " + fmtTime(t.duration);
    els.roadFill.style.width = "0%";
    els.progressTruck.style.left = "0%";

    if (t.audio_url){
      els.audioEl.src = t.audio_url;
      try { els.audioEl.load(); } catch(e){}
    }

    if (t.cover_url){
      els.cassetteArt.src = t.cover_url;
      els.cassetteArt.style.display = 'block';
    } else {
      els.cassetteArt.removeAttribute('src');
      els.cassetteArt.style.display = 'none';
    }
    renderPlaylist();
  }

  function updateProgressUI(){
    if (state.radioOn) return;
    if (!TRACKS.length) return;
    var t = TRACKS[state.index];
    var duration = (els.audioEl.duration && !isNaN(els.audioEl.duration)) ? els.audioEl.duration : (t.duration || 200);
    var currentTime = els.audioEl.currentTime || state.elapsed;
    var pct = Math.min(100, (currentTime / duration) * 100);
    els.roadFill.style.width = pct + "%";
    els.progressTruck.style.left = pct + "%";
    els.kmDone.textContent = Math.round((pct/100) * t.km);
    els.timeReadout.textContent = fmtTime(currentTime) + " / " + fmtTime(duration);
  }

  function tick(){
    if (state.radioOn || !TRACKS.length) return;
    if (!els.audioEl.paused) {
      state.elapsed = els.audioEl.currentTime;
    } else {
      state.elapsed += 0.25;
    }
    updateProgressUI();
  }

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
    els.playBtn.textContent = "⏸";
    els.cassette.classList.add('spin');
    
    var p = els.audioEl.play();
    if (p !== undefined){
      p.catch(function(err){
        console.warn("Audio playback prevented by browser policy:", err);
        state.playing = false;
        els.playBtn.textContent = "▶";
        els.cassette.classList.remove('spin');
      });
    }

    clearInterval(state.timer);
    state.timer = setInterval(tick, 250);
  }

  function pause(){
    state.playing = false;
    els.playBtn.textContent = "▶";
    els.cassette.classList.remove('spin');
    els.audioEl.pause();
    clearInterval(state.timer);
  }

  function togglePlay(){ state.playing ? pause() : play(); }

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
    loadTrack(state.index + 1);
    if (state.playing) play();
    else updateProgressUI();
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
    loadTrack(state.index - 1);
    if (state.playing) play();
    else updateProgressUI();
  }

  function honk(){
    els.hornAudio.currentTime = 0;
    els.hornAudio.play().catch(function(){});
    els.truckZone.classList.remove('honk');
    void els.truckZone.offsetWidth;
    els.truckZone.classList.add('honk');
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
    if (!SHAYARI.length) return;
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
        els.trackTitle.textContent = "Radio Mirchi 98.3 FM Live 📻";
        els.trackArtist.textContent = "Mirchi Murga & RJ Naved Comedy";
        els.audioEl.src = TRACKS[state.index].audio_url;
        try { els.audioEl.load(); } catch(e){}
        els.audioEl.play().catch(function(){});
      }
      return;
    }
    
    var idx = (liveRadioIdx + retryOffset) % stations.length;
    var radioStation = stations[idx];

    state.playing = true;
    els.playBtn.textContent = "⏸";
    els.cassette.classList.add('spin');
    els.trackTitle.textContent = radioStation.title;
    els.trackArtist.textContent = radioStation.artist;
    els.kmTotal.textContent = "LIVE";
    els.kmDone.textContent = "LIVE";
    els.timeReadout.textContent = "RADIO MIRCHI 98.3 LIVE 📻";
    els.roadFill.style.width = "100%";
    els.progressTruck.style.left = "100%";

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
    els.radioBtn.classList.toggle('active', state.radioOn);
    els.signage.classList.toggle('radio-on', state.radioOn);

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
        loadTrack(state.index);
        play();
      } else {
        pause();
      }
    }
  }

  function openSheet(){ els.playlistSheet.classList.add('open'); els.sheetBackdrop.classList.add('open'); }
  function closeSheet(){ els.playlistSheet.classList.remove('open'); els.sheetBackdrop.classList.remove('open'); }

  function updateClock(){
    var d = new Date();
    var h = d.getHours(), m = d.getMinutes(), s = d.getSeconds();
    var ampm = h >= 12 ? "pm" : "am";
    var h12 = h % 12; if (h12 === 0) h12 = 12;
    var mStr = m < 10 ? "0" + m : m;
    var sStr = s < 10 ? "0" + s : s;
    els.clock.innerHTML = h12 + ":" + mStr + ":" + sStr + '<span class="ampm">' + ampm + '</span>';
  }

  function driftListeners(){
    var delta = Math.round((Math.random()-0.55) * 14);
    state.listeners = Math.max(410, Math.min(920, state.listeners + delta));
    els.listenerCount.textContent = state.listeners;
  }

  // HTML5 Audio Event Listeners
  els.audioEl.addEventListener('timeupdate', updateProgressUI);
  els.audioEl.addEventListener('ended', function(){
    if (!state.radioOn) nextTrack();
  });

  els.playBtn.addEventListener('click', togglePlay);
  els.nextBtn.addEventListener('click', nextTrack);
  els.prevBtn.addEventListener('click', prevTrack);
  els.hornBtn.addEventListener('click', honk);
  els.radioBtn.addEventListener('click', toggleRadio);
  els.teaBtn.addEventListener('click', toggleTea);
  els.playlistBtn.addEventListener('click', openSheet);
  els.closePlaylist.addEventListener('click', closeSheet);
  els.sheetBackdrop.addEventListener('click', closeSheet);

  updateClock();
  setInterval(updateClock, 1000);
  setInterval(driftListeners, 3200);

  fetch(window.PICKUPWALA_API)
    .then(function(r){ return r.json(); })
    .then(function(data){
      TRACKS = data.tracks || [];
      if (data.shayari && data.shayari.length) SHAYARI = data.shayari;
      if (data.chai && data.chai.length) CHAI_MESSAGES = data.chai;
      state.shayariIdx = 0;
      showShayari(0);
      startShayariCycle(5200);
      if (TRACKS.length){
        loadTrack(0);
        updateProgressUI();
      } else {
        els.trackTitle.textContent = "कोई song उपलब्ध नहीं";
        els.trackArtist.textContent = "Admin panel से song add करें";
        renderPlaylist();
      }
    })
    .catch(function(){
      els.trackTitle.textContent = "Playlist लोड नहीं हुई";
      els.trackArtist.textContent = "API check करें";
    });
})();
