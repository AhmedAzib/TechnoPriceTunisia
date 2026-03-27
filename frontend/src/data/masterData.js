
// src/data/masterData.js
import tunisianetData from './tunisianet_clean.json';
import spacenetData from './spacenet_products.json';
import mytekData from './mytek_test.json';
import mytekMobileData from './mytek_mobiles.json';
import wikiData from './wiki_clean.json';

import fakeComponents from './fake_components.json';

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
      id: `COMP-${index}`, // Ensure unique IDs
      source: 'TechnoPrice Components'
  }))
];
