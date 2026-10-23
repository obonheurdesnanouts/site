
document.addEventListener('DOMContentLoaded', () => {
  // MENU DE NAVIGATION
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    const fermerMenu = () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Ouvrir le menu');
    };

    toggle.addEventListener('click', () => {
      const ouvert = nav.classList.toggle('open');

      toggle.setAttribute('aria-expanded', String(ouvert));
      toggle.setAttribute(
        'aria-label',
        ouvert ? 'Fermer le menu' : 'Ouvrir le menu'
      );
    });

    nav.querySelectorAll('a').forEach(lien => {
      lien.addEventListener('click', fermerMenu);
    });

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        fermerMenu();
        toggle.focus();
      }
    });

    document.addEventListener('click', event => {
      if (
        nav.classList.contains('open') &&
        !nav.contains(event.target) &&
        !toggle.contains(event.target)
      ) {
        fermerMenu();
      }
    });
  }

  // ANIMATIONS AU DÉFILEMENT
  const elementsReveal = document.querySelectorAll('.reveal');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });

    elementsReveal.forEach(element => observer.observe(element));
  } else {
    elementsReveal.forEach(element => {
      element.classList.add('visible');
    });
  }

  
  // AGRANDISSEMENT DES PHOTOS
  const modal = document.querySelector('.photo-modal');

  if (modal) {
    const modalImg = modal.querySelector('img');
    const closeButton = modal.querySelector('button');

    if (modalImg && closeButton) {
      const ouvrirPhoto = image => {
        modalImg.src = image.currentSrc || image.src;
        modalImg.alt = image.alt || 'Photo agrandie';
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        closeButton.focus();
      };

      const fermerPhoto = () => {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
        modalImg.removeAttribute('src');
        document.body.style.overflow = '';
      };

      // Écoute aussi les photos ajoutées après le chargement
      document.addEventListener('click', event => {
        const image = event.target.closest('img[data-enlarge]');

        if (image) {
          ouvrirPhoto(image);
        }
      });

      // Permet d'ouvrir une photo au clavier
      document.addEventListener('keydown', event => {
        const image = event.target.closest?.('img[data-enlarge]');

        if (
          image &&
          (event.key === 'Enter' || event.key === ' ')
        ) {
          event.preventDefault();
          ouvrirPhoto(image);
          return;
        }

        if (event.key === 'Escape' && modal.classList.contains('open')) {
          fermerPhoto();
        }
      });

      closeButton.addEventListener('click', fermerPhoto);

      modal.addEventListener('click', event => {
        if (event.target === modal) {
          fermerPhoto();
        }
      });
    }
  }


  // PARTAGE FACEBOOK
  document.querySelectorAll('[data-share-facebook]').forEach(bouton => {
    bouton.addEventListener('click', () => {
      const url = encodeURIComponent(window.location.href);

      window.open(
        'https://www.facebook.com/sharer/sharer.php?u=' + url,
        '_blank',
        'noopener,noreferrer,width=650,height=500'
      );
    });
  });

  // ANNÉE AUTOMATIQUE DANS LES PIEDS DE PAGE
  ['year', 'annee', 'current-year'].forEach(id => {
    const element = document.getElementById(id);

    if (element) {
      element.textContent = new Date().getFullYear();
    }
  });
});
