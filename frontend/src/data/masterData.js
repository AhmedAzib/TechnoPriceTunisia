
// src/data/masterData.js
import tunisianetData from './tunisianet_clean.json';
import spacenetData from './spacenet_products.json';
import mytekData from './mytek_test.json';
import mytekMobileData from './mytek_mobiles.json';
import wikiData from './wiki_clean.json';
import fakeComponents from './fake_components.json';

// Mobile-specific data sources
import tunisianetMobiles from './tunisianet_mobiles.json';
import tunisiatechMobiles from './tunisiatech_mobiles.json';
import wikiMobiles from './wiki_mobiles.json';
import tdiscountMobiles from './tdiscount_mobiles.json';
import spacenetMobiles from './spacenet_mobiles.json';
import samsungTunisie from './samsung_tunisie.json';

// Export the RAW merged list. 
// Normalization should happen in the components or hooks using normalizeProductData utility.
export const MASTER_DATA = [
  ...tunisianetData.map(p => ({ ...p, source: 'Tunisianet' })), 
  ...spacenetData.filter(p => {
        const t = p.title.toLowerCase();
        // Remove "Ghost" products requested by user (Step 9.6 & 9.7)
        return !t.includes('asus vivobook 15 x515ka') && 
               !t.includes('lenovo ideapad 1') &&
               !t.includes('hp 15-fd0421nk');
    }).map(p => ({ ...p, source: 'Spacenet' })),
  ...mytekData.map((p, index) => ({
      ...p,
      id: `MK-${index}`,
      source: 'MyTek'
  })),
  ...mytekMobileData.map((p, index) => ({
      ...p,
      id: `MK-MOB-${index}`,
      source: 'MyTek',
      category: 'Smartphone' // Explicit category for filtering
  })),
  ...wikiData.map(p => ({ ...p, source: 'Wiki' })),
  ...fakeComponents.map((p, index) => ({
      ...p,
      id: `COMP-${index}`,
      source: 'TechnoPrice Components'
  })),
  // Mobile stores
  ...tunisianetMobiles.map((p, index) => ({
      ...p,
      id: p.id || `TN-MOB-${index}`,
      source: 'Tunisianet',
      category: 'Smartphone'
  })),
  ...tunisiatechMobiles.map((p, index) => ({
      ...p,
      id: p.id || `TT-MOB-${index}`,
      source: 'TunisiaTech',
      category: 'Smartphone'
  })),
  ...wikiMobiles.map((p, index) => ({
      ...p,
      id: p.id || `WK-MOB-${index}`,
      source: 'Wiki',
      category: 'Smartphone'
  })),
  ...tdiscountMobiles.map((p, index) => ({
      ...p,
      id: p.id || `TD-MOB-${index}`,
      source: 'Tdiscount',
      category: 'Smartphone'
  })),
  ...spacenetMobiles.map((p, index) => ({
      ...p,
      id: p.id || `SN-MOB-${index}`,
      source: 'SpaceNet',
      category: 'Smartphone'
  })),
  ...samsungTunisie.map((p, index) => ({
      ...p,
      id: p.id || `ST-MOB-${index}`,
      source: 'Samsung Tunisie',
      category: 'Smartphone'
  }))
];
