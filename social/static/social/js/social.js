/**
 * Ghidora Social — Instagram Feed Interactions JS
 */

// Helper to retrieve CSRF token from DOM or cookies
function getCSRFToken() {
  const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (tokenInput) return tokenInput.value;
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, 10) === ('csrftoken=')) {
        cookieValue = decodeURIComponent(cookie.substring(10));
        break;
      }
    }
  }
  return cookieValue;
}

// -------------------------------------------------------------
// 1. AJAX Like / Unlike Toggle
// -------------------------------------------------------------
async function toggleLikeAJAX(postId) {
  const btn = document.getElementById(`like-btn-${postId}`);
  const countEl = document.getElementById(`like-count-${postId}`);
  if (!btn) return;

  const isLiked = btn.classList.contains('liked');
  
  // Optimistic UI update
  btn.classList.toggle('liked');
  const heartIcon = btn.querySelector('i');
  if (heartIcon) {
    heartIcon.className = isLiked ? 'ti ti-heart' : 'ti ti-heart-filled';
  }
  
  let currentCount = parseInt(countEl.innerText) || 0;
  countEl.innerText = isLiked ? Math.max(0, currentCount - 1) : currentCount + 1;

  try {
    const response = await fetch(`/social/post/${postId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Network error');
    const data = await response.json();

    // Sync with server state
    if (data.liked) {
      btn.classList.add('liked');
      if (heartIcon) heartIcon.className = 'ti ti-heart-filled';
    } else {
      btn.classList.remove('liked');
      if (heartIcon) heartIcon.className = 'ti ti-heart';
    }
    if (countEl && typeof data.like_count === 'number') {
      countEl.innerText = data.like_count;
    }
  } catch (err) {
    console.error('Like toggle failed:', err);
    // Revert optimistic update on failure
    btn.classList.toggle('liked', isLiked);
    if (heartIcon) heartIcon.className = isLiked ? 'ti ti-heart-filled' : 'ti ti-heart';
    countEl.innerText = currentCount;
  }
}

function quickLikePost(postId) {
  const btn = document.getElementById(`like-btn-${postId}`);
  if (btn && !btn.classList.contains('liked')) {
    toggleLikeAJAX(postId);
  }
}

// -------------------------------------------------------------
// 2. AJAX Comment Submission
// -------------------------------------------------------------
async function submitCommentAJAX(event, postId) {
  event.preventDefault();
  const input = document.getElementById(`comment-input-${postId}`);
  const listEl = document.getElementById(`comments-list-${postId}`);
  const parentInput = document.getElementById(`comment-parent-${postId}`);
  if (!input || !input.value.trim()) return;

  const content = input.value.trim();
  const parentId = parentInput ? parentInput.value : '';
  input.value = '';

  const submitBtn = document.getElementById(`comment-btn-${postId}`);
  if (submitBtn) submitBtn.disabled = true;

  try {
    const postBody = { content };
    if (parentId) postBody.parent_id = parentId;

    const response = await fetch(`/social/post/${postId}/comment/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams(postBody),
    });

    const data = await response.json();
    if (data.ok && data.comment) {
      const isReply = Boolean(data.comment.parent_id);
      const commentRow = document.createElement('div');
      commentRow.className = `ig-comment-row ${isReply ? 'ig-reply-row' : ''}`;
      commentRow.id = `comment-row-${data.comment.id}`;
      
      const formattedContent = formatSocialTextJS(data.comment.content);

      commentRow.innerHTML = `
        <div class="ig-comment-main">
          <a href="/social/profile/${escapeHTML(data.comment.author)}/" class="ig-bold-user">${escapeHTML(data.comment.author)}</a>
          <span class="ig-comment-text">${formattedContent}</span>
          <div class="ig-comment-meta">
            <span class="ig-comment-time">just now</span>
            <span class="ig-comment-likes-count" id="comment-like-count-${data.comment.id}"></span>
            <button type="button" class="ig-comment-reply-btn" onclick="prepareCommentReply(${postId}, ${data.comment.parent_id || data.comment.id}, '${escapeHTML(data.comment.author)}')">Reply</button>
            <button type="button" class="ig-comment-delete-btn" onclick="deleteCommentAJAX(${data.comment.id}, ${postId})" title="Delete comment">
              <i class="ti ti-trash"></i>
            </button>
          </div>
        </div>
        <button type="button" 
                class="ig-comment-like-btn" 
                id="comment-like-btn-${data.comment.id}" 
                onclick="toggleCommentLikeAJAX(${data.comment.id})" 
                title="Like comment">
          <i class="ti ti-heart"></i>
        </button>
      `;

      if (isReply) {
        const parentRow = document.getElementById(`comment-row-${data.comment.parent_id}`);
        if (parentRow && parentRow.nextSibling) {
          listEl.insertBefore(commentRow, parentRow.nextSibling);
        } else {
          listEl.appendChild(commentRow);
        }
      } else {
        listEl.appendChild(commentRow);
      }

      // Reset reply state if replying
      cancelCommentReply(postId);
    } else {
      alert(data.error || 'Failed to post comment.');
    }
  } catch (err) {
    console.error('Comment submit error:', err);
    alert('Failed to post comment. Please try again.');
  }
}

// Enable post button when typing comment
document.addEventListener('input', (e) => {
  if (e.target.classList.contains('ig-comment-input-field')) {
    const form = e.target.closest('form');
    if (form) {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = !e.target.value.trim();
    }
  }
});

function focusCommentInput(postId) {
  const input = document.getElementById(`comment-input-${postId}`);
  if (input) input.focus();
}

function expandComments(postId) {
  const hiddenRows = document.querySelectorAll(`#comments-list-${postId} .hidden-comment`);
  hiddenRows.forEach(row => row.classList.remove('hidden-comment'));
  const btn = document.getElementById(`view-comments-btn-${postId}`);
  if (btn) btn.style.display = 'none';
}

function expandCaption(postId) {
  const captionEl = document.getElementById(`caption-${postId}`);
  if (captionEl) captionEl.classList.remove('truncated');
  const moreBtn = captionEl ? captionEl.nextElementSibling : null;
  if (moreBtn && moreBtn.classList.contains('ig-more-btn')) {
    moreBtn.style.display = 'none';
  }
}

// -------------------------------------------------------------
// 3. Carousel Navigation
// -------------------------------------------------------------
const carouselPositions = {};

function slideCarousel(postId, direction) {
  const carousel = document.getElementById(`carousel-${postId}`);
  if (!carousel) return;
  const track = carousel.querySelector('.ig-carousel-track');
  const slides = carousel.querySelectorAll('.ig-carousel-slide');
  const dots = carousel.querySelectorAll('.ig-carousel-dots .dot');
  const badge = carousel.querySelector('.ig-carousel-badge');

  if (!slides.length) return;
  
  if (!(postId in carouselPositions)) {
    carouselPositions[postId] = 0;
  }

  carouselPositions[postId] += direction;
  if (carouselPositions[postId] < 0) carouselPositions[postId] = 0;
  if (carouselPositions[postId] >= slides.length) carouselPositions[postId] = slides.length - 1;

  const currentIdx = carouselPositions[postId];
  track.style.transform = `translateX(-${currentIdx * 100}%)`;

  dots.forEach((dot, i) => dot.classList.toggle('active', i === currentIdx));
  if (badge) badge.innerText = `${currentIdx + 1}/${slides.length}`;
}

// -------------------------------------------------------------
// 4. Menu & Share Actions
// -------------------------------------------------------------
function togglePostMenu(postId) {
  const popup = document.getElementById(`menu-popup-${postId}`);
  document.querySelectorAll('.ig-menu-popup').forEach(p => {
    if (p !== popup) p.classList.remove('show');
  });
  if (popup) popup.classList.toggle('show');
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.ig-menu-dropdown')) {
    document.querySelectorAll('.ig-menu-popup').forEach(p => p.classList.remove('show'));
  }
});

function sharePost(url) {
  const fullUrl = window.location.origin + url;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(fullUrl).then(() => {
      alert('Post link copied to clipboard!');
    });
  } else {
    prompt('Copy post URL:', fullUrl);
  }
}

// -------------------------------------------------------------
// 5. Likes Modal
// -------------------------------------------------------------
async function showLikesModal(postId) {
  const modal = document.getElementById('likesModal');
  const container = document.getElementById('likesListContainer');
  if (!modal || !container) return;

  container.innerHTML = '<div class="ig-loading">Loading...</div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/social/post/${postId}/likes/`);
    const data = await res.json();

    if (data.ok && data.likes && data.likes.length > 0) {
      container.innerHTML = data.likes.map(u => `
        <div style="display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid #262a36;">
          <div style="width:36px; height:36px; border-radius:50%; overflow:hidden; background:#262a36; display:flex; align-items:center; justify-content:center;">
            ${u.avatar_url ? `<img src="${u.avatar_url}" style="width:100%; height:100%; object-fit:cover;">` : `<span style="font-weight:700;">${u.username[0].toUpperCase()}</span>`}
          </div>
          <div>
            <a href="/social/profile/${u.username}/" style="color:#fff; font-weight:600; text-decoration:none;">${u.display_name}</a>
            ${u.is_driver ? '<span class="gs-badge-driver">DRIVER</span>' : ''}
            <div style="font-size:0.75rem; color:#9ca3af;">@${u.username}</div>
          </div>
        </div>
      `).join('');
    } else {
      container.innerHTML = '<div style="color:#9ca3af; text-align:center; padding:20px;">No likes yet.</div>';
    }
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; text-align:center; padding:20px;">Failed to load likes.</div>';
  }
}

function closeLikesModal() {
  const modal = document.getElementById('likesModal');
  if (modal) modal.style.display = 'none';
}

// -------------------------------------------------------------
// 6. Post & Story Upload Modals
// -------------------------------------------------------------
function openPostCreateModal() {
  document.getElementById('createPostModal').style.display = 'flex';
}
function closePostCreateModal() {
  document.getElementById('createPostModal').style.display = 'none';
}
function openStoryUploadModal() {
  document.getElementById('uploadStoryModal').style.display = 'flex';
}
function closeStoryUploadModal() {
  document.getElementById('uploadStoryModal').style.display = 'none';
}
function openChangePhotoModal() {
  const modal = document.getElementById('changePhotoModal');
  if (modal) modal.style.display = 'flex';
}
function closeChangePhotoModal() {
  const modal = document.getElementById('changePhotoModal');
  if (modal) modal.style.display = 'none';
}


function previewPostImages(e) {
  const container = document.getElementById('postImagePreviews');
  const selector = document.getElementById('postAspectSelector');
  if (!container) return;
  container.innerHTML = '';
  const files = e.target.files;

  if (files && files.length > 0) {
    if (selector) selector.style.display = 'flex';
    Array.from(files).forEach((file) => {
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      img.style.objectFit = 'contain';
      img.style.height = '70px';
      img.style.borderRadius = '6px';
      container.appendChild(img);
    });
  } else {
    if (selector) selector.style.display = 'none';
  }
}

function previewStoryImage(e) {
  const wrap = document.getElementById('storyPreviewWrap');
  const img = document.getElementById('storyPreviewImg');
  const selector = document.getElementById('storyAspectSelector');
  const file = e.target.files[0];

  if (file) {
    img.src = URL.createObjectURL(file);
    wrap.style.display = 'block';
    if (selector) selector.style.display = 'flex';
  }
}

function setPostAspect(ratio, btn) {
  const selector = document.getElementById('postAspectSelector');
  if (selector) {
    selector.querySelectorAll('.ig-aspect-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
  }

  const imgs = document.querySelectorAll('#postImagePreviews img');
  imgs.forEach((img) => {
    if (ratio === '1:1') {
      img.style.aspectRatio = '1/1';
      img.style.objectFit = 'cover';
      img.style.width = '70px';
      img.style.height = '70px';
    } else if (ratio === '4:5') {
      img.style.aspectRatio = '4/5';
      img.style.objectFit = 'cover';
      img.style.width = '64px';
      img.style.height = '80px';
    } else if (ratio === '16:9') {
      img.style.aspectRatio = '16/9';
      img.style.objectFit = 'cover';
      img.style.width = '100px';
      img.style.height = '56px';
    } else {
      img.style.aspectRatio = 'unset';
      img.style.objectFit = 'contain';
      img.style.width = 'auto';
      img.style.height = '70px';
    }
  });
}

function setStoryAspect(ratio, btn) {
  const selector = document.getElementById('storyAspectSelector');
  if (selector) {
    selector.querySelectorAll('.ig-aspect-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
  }

  const img = document.getElementById('storyPreviewImg');
  if (!img) return;

  if (ratio === '9:16') {
    img.style.aspectRatio = '9/16';
    img.style.objectFit = 'cover';
  } else if (ratio === '1:1') {
    img.style.aspectRatio = '1/1';
    img.style.objectFit = 'cover';
  } else {
    img.style.aspectRatio = 'unset';
    img.style.objectFit = 'contain';
  }
}


// -------------------------------------------------------------
// 7. Interactive Story Viewer
// -------------------------------------------------------------
let currentStoryGroup = [];
let currentStoryIdx = 0;
let storyTimer = null;

function openStoryViewer(userId, username, avatarUrl, stories) {
  if (!stories || !stories.length) return;

  currentStoryGroup = stories;
  currentStoryIdx = 0;

  const modal = document.getElementById('storyViewerModal');
  const userAvatar = document.getElementById('svUserAvatar');
  const usernameEl = document.getElementById('svUsername');

  if (avatarUrl) {
    userAvatar.src = avatarUrl;
    userAvatar.style.display = 'block';
  } else {
    userAvatar.style.display = 'none';
  }
  usernameEl.innerText = username;

  renderStorySlide();
  modal.style.display = 'flex';
}

function renderStorySlide() {
  if (storyTimer) clearInterval(storyTimer);

  const story = currentStoryGroup[currentStoryIdx];
  if (!story) {
    closeStoryViewer();
    return;
  }

  // Update image & caption
  document.getElementById('svStoryImg').src = story.media_url;
  document.getElementById('svTime').innerText = story.created_at || '';
  const capEl = document.getElementById('svCaption');
  if (story.caption) {
    capEl.innerText = story.caption;
    capEl.style.display = 'block';
  } else {
    capEl.style.display = 'none';
  }

  // Render progress segments
  const progressBar = document.getElementById('svProgressBar');
  progressBar.innerHTML = currentStoryGroup.map((_, idx) => `
    <div class="ig-sv-progress-segment">
      <div class="ig-sv-progress-fill" id="svFill-${idx}" style="width: ${idx < currentStoryIdx ? '100%' : '0%'};"></div>
    </div>
  `).join('');

  // Mark story as viewed via AJAX
  fetch(`/social/story/${story.id}/view/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
  }).catch(() => {});

  // Progress bar animation & auto-advance timer (5 seconds)
  let progress = 0;
  const currentFill = document.getElementById(`svFill-${currentStoryIdx}`);
  storyTimer = setInterval(() => {
    progress += 2;
    if (currentFill) currentFill.style.width = `${progress}%`;
    if (progress >= 100) {
      clearInterval(storyTimer);
      nextStorySlide();
    }
  }, 100);
}

function nextStorySlide() {
  if (currentStoryIdx < currentStoryGroup.length - 1) {
    currentStoryIdx++;
    renderStorySlide();
  } else {
    closeStoryViewer();
  }
}

function prevStorySlide() {
  if (currentStoryIdx > 0) {
    currentStoryIdx--;
    renderStorySlide();
  } else {
    renderStorySlide();
  }
}

function closeStoryViewer() {
  if (storyTimer) clearInterval(storyTimer);
  const modal = document.getElementById('storyViewerModal');
  if (modal) modal.style.display = 'none';
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

function formatSocialTextJS(text) {
  if (!text) return '';
  let escaped = escapeHTML(text);
  // Auto-link hashtags
  escaped = escaped.replace(/(^|\s)#([\w\d_]+)/g, (match, prefix, tag) => {
    return `${prefix}<a href="/social/explore/?q=%23${encodeURIComponent(tag)}" class="ig-hashtag">#${tag}</a>`;
  });
  // Auto-link mentions
  escaped = escaped.replace(/(^|\s)@([\w\d_]+)/g, (match, prefix, user) => {
    return `${prefix}<a href="/social/profile/${encodeURIComponent(user)}/" class="ig-mention">@${user}</a>`;
  });
  return escaped;
}

// -------------------------------------------------------------
// 8. Comment Replies & Likes
// -------------------------------------------------------------
function prepareCommentReply(postId, commentId, username) {
  const parentInput = document.getElementById(`comment-parent-${postId}`);
  const indicator = document.getElementById(`reply-indicator-${postId}`);
  const usernameEl = document.getElementById(`reply-username-${postId}`);
  const input = document.getElementById(`comment-input-${postId}`);

  if (parentInput) parentInput.value = commentId;
  if (usernameEl) usernameEl.innerText = `@${username}`;
  if (indicator) indicator.style.display = 'flex';

  if (input) {
    if (!input.value.startsWith(`@${username} `)) {
      input.value = `@${username} ` + input.value.replace(/^@\w+\s*/, '');
    }
    input.focus();
  }
}

function cancelCommentReply(postId) {
  const parentInput = document.getElementById(`comment-parent-${postId}`);
  const indicator = document.getElementById(`reply-indicator-${postId}`);
  const input = document.getElementById(`comment-input-${postId}`);

  if (parentInput) parentInput.value = '';
  if (indicator) indicator.style.display = 'none';
  if (input && input.value.startsWith('@')) {
    input.value = input.value.replace(/^@\w+\s*/, '');
  }
}

async function toggleCommentLikeAJAX(commentId) {
  const btn = document.getElementById(`comment-like-btn-${commentId}`);
  const countEl = document.getElementById(`comment-like-count-${commentId}`);
  if (!btn) return;

  const isLiked = btn.classList.contains('liked');
  btn.classList.toggle('liked');
  const icon = btn.querySelector('i');
  if (icon) {
    icon.className = isLiked ? 'ti ti-heart' : 'ti ti-heart-filled';
  }

  try {
    const res = await fetch(`/social/comment/${commentId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    const data = await res.json();
    if (data.ok) {
      if (data.liked) {
        btn.classList.add('liked');
        if (icon) icon.className = 'ti ti-heart-filled';
      } else {
        btn.classList.remove('liked');
        if (icon) icon.className = 'ti ti-heart';
      }
      if (countEl) {
        countEl.innerText = data.like_count > 0 ? `${data.like_count} ${data.like_count === 1 ? 'like' : 'likes'}` : '';
      }
    }
  } catch (err) {
    console.error('Comment like failed:', err);
    btn.classList.toggle('liked', isLiked);
    if (icon) icon.className = isLiked ? 'ti ti-heart-filled' : 'ti ti-heart';
  }
}

async function deleteCommentAJAX(commentId, postId) {
  if (!confirm('Delete this comment?')) return;

  try {
    const res = await fetch(`/social/comment/${commentId}/delete/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    const data = await res.json();
    if (data.ok) {
      const row = document.getElementById(`comment-row-${commentId}`);
      if (row) row.remove();
    } else {
      alert(data.error || 'Failed to delete comment.');
    }
  } catch (err) {
    console.error('Delete comment failed:', err);
    alert('Network error deleting comment.');
  }
}

// -------------------------------------------------------------
// 9. Bookmark / Save Post Toggle
// -------------------------------------------------------------
async function toggleSaveAJAX(postId) {
  const btn = document.getElementById(`save-btn-${postId}`);
  if (!btn) return;

  const isSaved = btn.classList.contains('saved');
  btn.classList.toggle('saved');
  const icon = btn.querySelector('i');
  if (icon) {
    icon.className = isSaved ? 'ti ti-bookmark' : 'ti ti-bookmark-filled';
  }

  try {
    const res = await fetch(`/social/post/${postId}/save/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    const data = await res.json();
    if (data.ok) {
      if (data.saved) {
        btn.classList.add('saved');
        if (icon) icon.className = 'ti ti-bookmark-filled';
      } else {
        btn.classList.remove('saved');
        if (icon) icon.className = 'ti ti-bookmark';
      }
    }
  } catch (err) {
    console.error('Save toggle failed:', err);
    btn.classList.toggle('saved', isSaved);
    if (icon) icon.className = isSaved ? 'ti ti-bookmark-filled' : 'ti ti-bookmark';
  }
}

// -------------------------------------------------------------
// 10. Real Follow / Unfollow Toggle
// -------------------------------------------------------------
async function toggleFollowAJAX(username, btnEl = null) {
  const btn = btnEl || document.getElementById('profileFollowBtn');
  const followersCountEl = document.getElementById('profileFollowersCount');
  const isFollowing = btn ? (btn.innerText.trim().toLowerCase() === 'following' || btn.classList.contains('ig-btn-profile')) : false;

  if (btn) {
    btn.innerText = isFollowing ? 'Follow' : 'Following';
    btn.classList.toggle('ig-btn-primary', isFollowing);
    btn.classList.toggle('ig-btn-profile', !isFollowing);
  }

  if (followersCountEl) {
    let count = parseInt(followersCountEl.innerText) || 0;
    followersCountEl.innerText = isFollowing ? Math.max(0, count - 1) : count + 1;
  }

  try {
    const res = await fetch(`/social/user/${encodeURIComponent(username)}/follow/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    const data = await res.json();
    if (data.ok) {
      if (btn) {
        btn.innerText = data.following ? 'Following' : 'Follow';
        btn.classList.toggle('ig-btn-primary', !data.following);
        btn.classList.toggle('ig-btn-profile', data.following);
      }
      if (followersCountEl && typeof data.follower_count === 'number') {
        followersCountEl.innerText = data.follower_count;
      }
    }
  } catch (err) {
    console.error('Follow toggle failed:', err);
    if (btn) {
      btn.innerText = isFollowing ? 'Following' : 'Follow';
      btn.classList.toggle('ig-btn-primary', !isFollowing);
      btn.classList.toggle('ig-btn-profile', isFollowing);
    }
  }
}

// -------------------------------------------------------------
// 11. Followers & Following Modals
// -------------------------------------------------------------
async function openFollowersModal(username) {
  const modal = document.getElementById('userListModal');
  const title = document.getElementById('userListModalTitle');
  const body = document.getElementById('userListModalBody');
  if (!modal || !body) return;

  if (title) title.innerText = 'Followers';
  body.innerHTML = '<div style="text-align:center; padding:24px; color:var(--ig-text-muted);"><i class="ti ti-loader" style="font-size:1.8rem;"></i><p style="margin:6px 0 0;">Loading followers...</p></div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/social/api/followers/${encodeURIComponent(username)}/`);
    const data = await res.json();
    if (data.ok) {
      renderUserListItems(body, data.followers, 'No followers yet');
    }
  } catch (err) {
    body.innerHTML = '<div style="text-align:center; padding:20px; color:var(--danger);">Failed to load followers.</div>';
  }
}

async function openFollowingModal(username) {
  const modal = document.getElementById('userListModal');
  const title = document.getElementById('userListModalTitle');
  const body = document.getElementById('userListModalBody');
  if (!modal || !body) return;

  if (title) title.innerText = 'Following';
  body.innerHTML = '<div style="text-align:center; padding:24px; color:var(--ig-text-muted);"><i class="ti ti-loader" style="font-size:1.8rem;"></i><p style="margin:6px 0 0;">Loading following...</p></div>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/social/api/following/${encodeURIComponent(username)}/`);
    const data = await res.json();
    if (data.ok) {
      renderUserListItems(body, data.following, 'Not following anyone yet');
    }
  } catch (err) {
    body.innerHTML = '<div style="text-align:center; padding:20px; color:var(--danger);">Failed to load following.</div>';
  }
}

function renderUserListItems(container, users, emptyMsg) {
  if (!users || !users.length) {
    container.innerHTML = `<div style="text-align:center; padding:30px 10px; color:var(--ig-text-muted);">${emptyMsg}</div>`;
    return;
  }

  container.innerHTML = users.map(u => `
    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.06);">
      <a href="/social/profile/${escapeHTML(u.username)}/" style="display:flex; align-items:center; gap:12px; text-decoration:none; color:inherit; flex:1; min-width:0;" onclick="closeUserListModal()">
        <div style="width:40px; height:40px; border-radius:50%; overflow:hidden; background:rgba(255,255,255,0.1); flex-shrink:0; display:flex; align-items:center; justify-content:center;">
          ${u.avatar_url ? `<img src="${escapeHTML(u.avatar_url)}" style="width:100%; height:100%; object-fit:cover;">` : `<span style="font-weight:700;">${escapeHTML(u.username[0].toUpperCase())}</span>`}
        </div>
        <div style="min-width:0; overflow:hidden;">
          <div style="font-weight:600; font-size:0.9rem; color:var(--text-hi); display:flex; align-items:center; gap:4px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">
            ${escapeHTML(u.display_name)}
            ${u.is_driver ? '<span class="gs-badge-driver" style="font-size:0.65rem;">DRIVER</span>' : ''}
          </div>
          <div style="font-size:0.75rem; color:var(--text-lo); text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">@${escapeHTML(u.username)}</div>
        </div>
      </a>
      <div>
        <button type="button" 
                class="${u.is_following ? 'ig-btn-profile' : 'ig-btn-primary'}" 
                style="padding:6px 14px; font-size:0.8rem; border-radius:8px;"
                onclick="toggleFollowAJAX('${escapeHTML(u.username)}', this)">
          ${u.is_following ? 'Following' : 'Follow'}
        </button>
      </div>
    </div>
  `).join('');
}

function closeUserListModal() {
  const modal = document.getElementById('userListModal');
  if (modal) modal.style.display = 'none';
}

// -------------------------------------------------------------
// 12. Real Activity / Notifications Feed
// -------------------------------------------------------------
async function openNotificationsModal() {
  const modal = document.getElementById('notificationsModalOverlay');
  const container = document.getElementById('notificationsListContainer');
  if (!modal) return;

  modal.style.display = 'flex';
  if (container) {
    container.innerHTML = '<div style="text-align:center; padding:30px 10px; color:var(--ig-text-muted);"><i class="ti ti-loader" style="font-size:2rem; margin-bottom:8px; display:block;"></i><p style="margin:0;">Loading activity...</p></div>';
  }

  try {
    const res = await fetch('/social/api/notifications/');
    const data = await res.json();
    if (data.ok && container) {
      if (!data.notifications || !data.notifications.length) {
        container.innerHTML = `
          <div style="text-align:center; padding:40px 16px; color:var(--ig-text-muted);">
            <i class="ti ti-bell-off" style="font-size:2.5rem; color:var(--ig-gold); margin-bottom:10px; display:block; opacity:0.8;"></i>
            <h4 style="margin:0 0 4px; color:var(--text-hi);">No Activity Yet</h4>
            <p style="margin:0; font-size:0.85rem;">When people like your updates, comment, or follow you, you'll see them here.</p>
          </div>
        `;
      } else {
        container.innerHTML = data.notifications.map(n => `
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 4px; border-bottom:1px solid rgba(255,255,255,0.06); ${!n.is_read ? 'background:rgba(63,164,255,0.06); border-radius:8px;' : ''}">
            <a href="/social/profile/${escapeHTML(n.sender.username)}/" style="display:flex; align-items:center; gap:10px; text-decoration:none; color:inherit; flex:1; min-width:0;" onclick="closeNotificationsModal()">
              <div style="width:38px; height:38px; border-radius:50%; overflow:hidden; background:rgba(255,255,255,0.1); flex-shrink:0; display:flex; align-items:center; justify-content:center;">
                ${n.sender.avatar_url ? `<img src="${escapeHTML(n.sender.avatar_url)}" style="width:100%; height:100%; object-fit:cover;">` : `<span style="font-weight:700;">${escapeHTML(n.sender.username[0].toUpperCase())}</span>`}
              </div>
              <div style="font-size:0.85rem; line-height:1.4; color:var(--text-hi);">
                <strong>${escapeHTML(n.sender.username)}</strong> ${escapeHTML(n.text)}
                <div style="font-size:0.75rem; color:var(--text-lo); margin-top:2px;">${escapeHTML(n.created_at)}</div>
              </div>
            </a>
            ${n.post_id ? `
              <a href="/social/post/${n.post_id}/" style="flex-shrink:0; text-decoration:none;" onclick="closeNotificationsModal()">
                ${n.post_image_url ? `<img src="${escapeHTML(n.post_image_url)}" style="width:40px; height:40px; border-radius:6px; object-fit:cover;">` : `<div style="width:40px; height:40px; border-radius:6px; background:rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:center; color:var(--blue-soft);"><i class="ti ti-file-text"></i></div>`}
              </a>
            ` : ''}
          </div>
        `).join('');
      }

      // Update badge if unread
      const badge = document.getElementById('notifBadge');
      if (badge) {
        if (data.unread_count > 0) {
          badge.innerText = data.unread_count;
          badge.style.display = 'inline-flex';
        } else {
          badge.style.display = 'none';
        }
      }
    }
  } catch (err) {
    if (container) container.innerHTML = '<div style="color:var(--danger); text-align:center; padding:20px;">Failed to load activity.</div>';
  }
}

function closeNotificationsModal() {
  const modal = document.getElementById('notificationsModalOverlay');
  if (modal) modal.style.display = 'none';
}

async function markAllNotificationsRead() {
  try {
    const res = await fetch('/social/api/notifications/read/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    const data = await res.json();
    if (data.ok) {
      const badge = document.getElementById('notifBadge');
      if (badge) badge.style.display = 'none';
      const container = document.getElementById('notificationsListContainer');
      if (container) {
        container.querySelectorAll('div').forEach(el => {
          el.style.background = 'transparent';
        });
      }
    }
  } catch (err) {
    console.error('Mark read failed:', err);
  }
}

// -------------------------------------------------------------
// 13. Debounced Live Search (Users & Hashtags)
// -------------------------------------------------------------
let searchDebounceTimer = null;

function handleSearchDebounce(e) {
  const query = e.target.value.trim();
  const container = document.getElementById('searchResultsContainer');
  if (!container) return;

  if (searchDebounceTimer) clearTimeout(searchDebounceTimer);

  if (!query) {
    container.innerHTML = `
      <div style="text-align:center; padding:30px 10px; color:var(--ig-text-muted);">
        <i class="ti ti-search" style="font-size:2rem; margin-bottom:8px; display:block; opacity:0.5;"></i>
        <p style="margin:0; font-size:0.88rem;">Search for drivers, clients, transport updates, or #hashtags</p>
      </div>
    `;
    return;
  }

  container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--ig-text-muted);"><i class="ti ti-loader" style="font-size:1.8rem;"></i></div>';

  searchDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/social/api/search/?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      if (data.ok) {
        let html = '';

        // Render Users
        if (data.users && data.users.length > 0) {
          html += '<div style="font-size:0.75rem; font-weight:700; color:var(--text-lo); text-transform:uppercase; margin-bottom:6px; letter-spacing:0.05em;">Profiles</div>';
          html += data.users.map(u => `
            <a href="/social/profile/${escapeHTML(u.username)}/" style="display:flex; align-items:center; gap:12px; padding:8px 0; text-decoration:none; color:inherit; border-bottom:1px solid rgba(255,255,255,0.04);" onclick="closeSearchModal()">
              <div style="width:36px; height:36px; border-radius:50%; overflow:hidden; background:rgba(255,255,255,0.1); flex-shrink:0; display:flex; align-items:center; justify-content:center;">
                ${u.avatar_url ? `<img src="${escapeHTML(u.avatar_url)}" style="width:100%; height:100%; object-fit:cover;">` : `<span style="font-weight:700;">${escapeHTML(u.username[0].toUpperCase())}</span>`}
              </div>
              <div>
                <div style="font-weight:600; font-size:0.9rem; color:var(--text-hi); display:flex; align-items:center; gap:4px;">
                  ${escapeHTML(u.display_name)}
                  ${u.is_driver ? '<span class="gs-badge-driver" style="font-size:0.65rem;">DRIVER</span>' : ''}
                </div>
                <div style="font-size:0.75rem; color:var(--text-lo);">@${escapeHTML(u.username)}</div>
              </div>
            </a>
          `).join('');
        }

        // Render Hashtags
        if (data.hashtags && data.hashtags.length > 0) {
          html += '<div style="font-size:0.75rem; font-weight:700; color:var(--text-lo); text-transform:uppercase; margin:14px 0 6px; letter-spacing:0.05em;">Tags & Routes</div>';
          html += data.hashtags.map(h => `
            <a href="/social/explore/?q=%23${encodeURIComponent(h.tag)}" style="display:flex; align-items:center; gap:12px; padding:8px 0; text-decoration:none; color:inherit; border-bottom:1px solid rgba(255,255,255,0.04);" onclick="closeSearchModal()">
              <div style="width:36px; height:36px; border-radius:50%; background:rgba(63,164,255,0.12); flex-shrink:0; display:flex; align-items:center; justify-content:center; color:var(--blue-soft);">
                <i class="ti ti-hash" style="font-size:1.2rem;"></i>
              </div>
              <div>
                <div style="font-weight:600; font-size:0.9rem; color:var(--blue-soft);">#${escapeHTML(h.tag)}</div>
                <div style="font-size:0.75rem; color:var(--text-lo);">${h.count} post${h.count === 1 ? '' : 's'}</div>
              </div>
            </a>
          `).join('');
        }

        if (!html) {
          html = `<div style="text-align:center; padding:30px 10px; color:var(--ig-text-muted);">No profiles or tags matching "<strong>${escapeHTML(query)}</strong>"</div>`;
        }

        container.innerHTML = html;
      }
    } catch (err) {
      container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--danger);">Error searching.</div>';
    }
  }, 250);
}

function openSearchModal() {
  const modal = document.getElementById('searchModalOverlay');
  if (modal) {
    modal.style.display = 'flex';
    const input = document.getElementById('searchInputField');
    if (input) {
      input.focus();
      input.value = '';
      handleSearchDebounce({ target: input });
    }
  }
}

function closeSearchModal() {
  const modal = document.getElementById('searchModalOverlay');
  if (modal) modal.style.display = 'none';
}

// -------------------------------------------------------------
// 14. Share Post Modal & Direct Message
// -------------------------------------------------------------
function openShareModal(postUrl, postId) {
  const modal = document.getElementById('shareModal');
  const urlInput = document.getElementById('sharePostUrl');
  const idInput = document.getElementById('sharePostId');
  const statusEl = document.getElementById('shareDmStatus');

  const fullUrl = window.location.origin + postUrl;
  if (urlInput) urlInput.value = fullUrl;
  if (idInput) idInput.value = postId;
  if (statusEl) statusEl.style.display = 'none';

  if (modal) modal.style.display = 'flex';
}

function closeShareModal() {
  const modal = document.getElementById('shareModal');
  if (modal) modal.style.display = 'none';
}

function copyShareModalLink() {
  const urlInput = document.getElementById('sharePostUrl');
  if (urlInput && urlInput.value) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(urlInput.value).then(() => {
        alert('Link copied to clipboard!');
      });
    } else {
      prompt('Copy post URL:', urlInput.value);
    }
  }
}

function copyPostLink(postUrl) {
  const fullUrl = window.location.origin + postUrl;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(fullUrl).then(() => {
      alert('Link copied to clipboard!');
    });
  } else {
    prompt('Copy post URL:', fullUrl);
  }
}

function shareOnWhatsApp() {
  const urlInput = document.getElementById('sharePostUrl');
  const url = urlInput ? urlInput.value : window.location.href;
  const text = `Check out this transport update on Ghidora: ${url}`;
  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
}

async function sendPostViaDMAJAX() {
  const usernameInput = document.getElementById('shareDmUsernameInput');
  const idInput = document.getElementById('sharePostId');
  const statusEl = document.getElementById('shareDmStatus');

  const username = usernameInput ? usernameInput.value.trim().replace(/^@/, '') : '';
  const postId = idInput ? idInput.value : '';

  if (!username || !postId) {
    if (statusEl) {
      statusEl.style.display = 'block';
      statusEl.style.color = 'var(--danger)';
      statusEl.innerText = 'Please enter a valid recipient username.';
    }
    return;
  }

  try {
    const res = await fetch('/social/api/share/dm/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams({ recipient_username: username, post_id: postId }),
    });
    const data = await res.json();
    if (data.ok) {
      if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.style.color = 'var(--cyan)';
        statusEl.innerText = `Sent to @${username} via Direct Message!`;
      }
      if (usernameInput) usernameInput.value = '';
      setTimeout(closeShareModal, 1200);
    } else {
      if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.style.color = 'var(--danger)';
        statusEl.innerText = data.error || 'Failed to send DM.';
      }
    }
  } catch (err) {
    if (statusEl) {
      statusEl.style.display = 'block';
      statusEl.style.color = 'var(--danger)';
      statusEl.innerText = 'Network error sending DM.';
    }
  }
}

// -------------------------------------------------------------
// 15. Real Moderation Report Modal
// -------------------------------------------------------------
function openReportModal(targetType, targetId) {
  const modal = document.getElementById('reportModal');
  const typeInput = document.getElementById('reportTargetType');
  const idInput = document.getElementById('reportTargetId');
  const detailsInput = document.getElementById('reportDetailsInput');

  if (typeInput) typeInput.value = targetType;
  if (idInput) idInput.value = targetId;
  if (detailsInput) detailsInput.value = '';

  if (modal) modal.style.display = 'flex';
}

function closeReportModal() {
  const modal = document.getElementById('reportModal');
  if (modal) modal.style.display = 'none';
}

async function submitReportAJAX(e) {
  e.preventDefault();
  const typeInput = document.getElementById('reportTargetType');
  const idInput = document.getElementById('reportTargetId');
  const reasonSelect = document.getElementById('reportReasonSelect');
  const detailsInput = document.getElementById('reportDetailsInput');

  const postBody = {
    target_type: typeInput ? typeInput.value : 'post',
    target_id: idInput ? idInput.value : '0',
    reason: reasonSelect ? reasonSelect.value : 'other',
    details: detailsInput ? detailsInput.value : '',
  };

  try {
    const res = await fetch('/social/api/report/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams(postBody),
    });
    const data = await res.json();
    if (data.ok) {
      alert('Thank you. Your report has been submitted to the Ghidora Moderation Team.');
      closeReportModal();
    } else {
      alert(data.error || 'Failed to submit report.');
    }
  } catch (err) {
    alert('Network error submitting report.');
  }
}

// -------------------------------------------------------------
// 16. Story Reactions & Viewers
// -------------------------------------------------------------
async function reactStoryAJAX(storyId, emoji) {
  try {
    await fetch(`/social/api/story/${storyId}/react/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams({ reaction: emoji }),
    });
    // Floating reaction feedback
    showFloatingReaction(emoji);
  } catch (err) {
    console.error('Story react error:', err);
  }
}

function showFloatingReaction(emoji) {
  const floater = document.createElement('div');
  floater.innerText = emoji;
  floater.style.position = 'fixed';
  floater.style.bottom = '100px';
  floater.style.left = '50%';
  floater.style.transform = 'translateX(-50%)';
  floater.style.fontSize = '2.5rem';
  floater.style.zIndex = '100005';
  floater.style.animation = 'floatUp 1s ease-out forwards';
  document.body.appendChild(floater);
  setTimeout(() => floater.remove(), 1000);
}

async function openStoryViewersModal(storyId) {
  const modal = document.getElementById('storyViewersModal');
  const list = document.getElementById('storyViewersList');
  if (!modal || !list) return;

  modal.style.display = 'flex';
  list.innerHTML = '<div style="text-align:center; padding:20px; color:var(--ig-text-muted);">Loading viewers...</div>';

  try {
    const res = await fetch(`/social/api/story/${storyId}/viewers/`);
    const data = await res.json();
    if (data.ok) {
      if (!data.viewers || !data.viewers.length) {
        list.innerHTML = '<div style="text-align:center; padding:24px; color:var(--ig-text-muted);">No views yet.</div>';
      } else {
        list.innerHTML = data.viewers.map(v => `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="display:flex; align-items:center; gap:10px;">
              <div style="width:34px; height:34px; border-radius:50%; overflow:hidden; background:rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center;">
                ${v.avatar_url ? `<img src="${escapeHTML(v.avatar_url)}" style="width:100%; height:100%; object-fit:cover;">` : `<span style="font-weight:700;">${escapeHTML(v.username[0].toUpperCase())}</span>`}
              </div>
              <div>
                <div style="font-weight:600; font-size:0.88rem; color:var(--text-hi);">${escapeHTML(v.display_name)}</div>
                <div style="font-size:0.75rem; color:var(--text-lo);">@${escapeHTML(v.username)} • ${escapeHTML(v.viewed_at)}</div>
              </div>
            </div>
            ${v.reactions && v.reactions.length ? `<div>${v.reactions.join(' ')}</div>` : ''}
          </div>
        `).join('');
      }
    }
  } catch (err) {
    list.innerHTML = '<div style="text-align:center; padding:20px; color:var(--danger);">Error loading viewers.</div>';
  }
}

function closeStoryViewersModal() {
  const modal = document.getElementById('storyViewersModal');
  if (modal) modal.style.display = 'none';
}

// -------------------------------------------------------------
// 17. Navigation & Profile Helpers
// -------------------------------------------------------------
function toggleProfileMenu(e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById('profileDropdownMenu');
  if (dropdown) dropdown.classList.toggle('show');
}

document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('profileDropdownMenu');
  if (dropdown && !e.target.closest('#profileDropdownMenu') && !e.target.closest('.ig-menu-trigger')) {
    dropdown.classList.remove('show');
  }

  const gsDropdown = document.getElementById('gsProfileDropdown');
  if (gsDropdown && !e.target.closest('#gsProfileDropdown') && !e.target.closest('.gs-user-chip')) {
    gsDropdown.classList.remove('open');
  }
});

function toggleGsProfileDropdown(e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById('gsProfileDropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

// Global Keyboard Shortcut: '/' triggers Search modal
document.addEventListener('keydown', (e) => {
  if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
    e.preventDefault();
    if (typeof openSearchModal === 'function') {
      openSearchModal();
    }
  }
});

// Auto-trigger post creation modal if ?compose=1 in URL
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('compose') === '1') {
    if (typeof openPostCreateModal === 'function') {
      openPostCreateModal();
    }
  }
});


