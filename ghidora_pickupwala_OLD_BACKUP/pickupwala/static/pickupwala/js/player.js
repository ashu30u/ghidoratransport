(function(){
  var TRACKS = [];
  var SHAYARI = ["लोड हो रहा है…"];
  var state = { index:0, playing:false, elapsed:0, radioOn:false, timer:null, shayariIdx:0, listeners:614 };

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
    player: document.getElementById('player')
  };

  function fmtTime(sec){
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
    els.audioEl.src = t.audio_url;
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
    if (!TRACKS.length) return;
    var t = TRACKS[state.index];
    var pct = Math.min(100, (state.elapsed / t.duration) * 100);
    els.roadFill.style.width = pct + "%";
    els.progressTruck.style.left = pct + "%";
    els.kmDone.textContent = Math.round((pct/100) * t.km);
    els.timeReadout.textContent = fmtTime(state.elapsed) + " / " + fmtTime(t.duration);
  }

  function tick(){
    if (!TRACKS.length) return;
    state.elapsed += 0.25;
    var t = TRACKS[state.index];
    if (state.elapsed >= t.duration){ nextTrack(); return; }
    updateProgressUI();
  }

  function play(){
    if (!TRACKS.length) return;
    state.playing = true;
    els.playBtn.textContent = "⏸";
    els.cassette.classList.add('spin');
    els.audioEl.play().catch(function(){});
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
  function nextTrack(){ loadTrack(state.index + 1); if (state.playing) play(); else updateProgressUI(); }
  function prevTrack(){ loadTrack(state.index - 1); if (state.playing) play(); else updateProgressUI(); }

  function honk(){
    els.hornAudio.currentTime = 0;
    els.hornAudio.play().catch(function(){});
    els.truckZone.classList.remove('honk');
    void els.truckZone.offsetWidth;
    els.truckZone.classList.add('honk');
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
  function toggleRadio(){
    state.radioOn = !state.radioOn;
    els.radioBtn.classList.toggle('active', state.radioOn);
    els.signage.classList.toggle('radio-on', state.radioOn);
    els.radioClickAudio.currentTime = 0;
    els.radioClickAudio.play().catch(function(){});
    startShayariCycle(state.radioOn ? 2600 : 5200);
  }

  function openSheet(){ els.playlistSheet.classList.add('open'); els.sheetBackdrop.classList.add('open'); }
  function closeSheet(){ els.playlistSheet.classList.remove('open'); els.sheetBackdrop.classList.remove('open'); }

  function updateClock(){
    var d = new Date();
    var h = d.getHours(), m = d.getMinutes();
    var ampm = h >= 12 ? "pm" : "am";
    var h12 = h % 12; if (h12 === 0) h12 = 12;
    els.clock.innerHTML = h12 + ":" + (m<10?"0":"") + m + '<span class="ampm">' + ampm + '</span>';
  }

  function driftListeners(){
    var delta = Math.round((Math.random()-0.55) * 14);
    state.listeners = Math.max(410, Math.min(920, state.listeners + delta));
    els.listenerCount.textContent = state.listeners;
  }

  els.playBtn.addEventListener('click', togglePlay);
  els.nextBtn.addEventListener('click', nextTrack);
  els.prevBtn.addEventListener('click', prevTrack);
  els.hornBtn.addEventListener('click', honk);
  els.radioBtn.addEventListener('click', toggleRadio);
  els.teaBtn.addEventListener('click', pause);
  els.playlistBtn.addEventListener('click', openSheet);
  els.closePlaylist.addEventListener('click', closeSheet);
  els.sheetBackdrop.addEventListener('click', closeSheet);

  updateClock();
  setInterval(updateClock, 15000);
  setInterval(driftListeners, 3200);

  // ---- Pull the live playlist + shayari straight from the admin-backed API ----
  fetch(window.PICKUPWALA_API)
    .then(function(r){ return r.json(); })
    .then(function(data){
      TRACKS = data.tracks || [];
      if (data.shayari && data.shayari.length) SHAYARI = data.shayari;
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
