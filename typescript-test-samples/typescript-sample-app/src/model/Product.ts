// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export interface Product {
  id: string;
  name: string;
  price: number;
}

export interface MetaProduct extends Product {
  timeCreated?: string;
  timeQueued?: string;
  timeStored?: string;
}

export type AnyProduct = Product | MetaProduct;
