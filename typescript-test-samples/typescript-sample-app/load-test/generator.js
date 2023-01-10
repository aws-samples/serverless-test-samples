// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

const crypto = require('crypto');

const COLORS = [
  "Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Pink", "Brown",
  "Black", "White", "Gray", "Silver", "Gold", "Cyan", "Magenta", "Maroon",
  "Navy", "Olive", "Teal", "Aqua", "Lime", "Coral", "Aquamarine",
  "Turquoise", "Violet", "Indigo", "Plum", "Crimson", "Salmon", "Coral",
  "Khaki", "Beige",
];

const PRODUCTS = [
  "Shoes", "Sweatshirts", "Hats", "Pants", "Shirts", "T-Shirts", "Trousers",
  "Jackets", "Shorts", "Skirts", "Dresses", "Coats", "Jeans", "Blazers",
  "Socks", "Gloves", "Belts", "Bags", "Shoes", "Sunglasses", "Watches",
  "Jewelry", "Ties", "Hair Accessories", "Makeup", "Accessories",
];

module.exports = {
  generateProduct: function(context, events, done) {
      const color = COLORS[Math.floor(Math.random() * COLORS.length)];
    const name = PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)];

    context.vars.id = crypto.randomUUID();
    context.vars.name =  `${color} ${name}`;
    context.vars.price = Math.round(Math.random() * 10000) / 100;

    return done();
  },
};