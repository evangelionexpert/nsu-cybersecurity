// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {Shop, Product, ProductInformation} from "../src/Shop.sol";

contract ShopTest is Test {
    Shop shop;

    address owner = makeAddr("owner");
    address buyer = makeAddr("buyer");

    struct ProductPair {
        ProductInformation info;
        Product product;
    }

    ProductPair[] private expectedProducts;

    constructor() {
        ProductPair memory prod0 = ProductPair(
            ProductInformation(1, "Knight Rider (1982)", 3 ether),
            Product("wioo wioo speaking Pontiac")
        );

        ProductPair memory prod1 = ProductPair(
            ProductInformation(7, "Back to the future (1985)", 5 ether),
            Product("wioo wioo flying Delorean")
        );

        ProductPair memory prod2 = ProductPair(
            ProductInformation(5, "Pulp Fiction (1994)", 4 ether),
            Product("wioo wioo burgers")
        );

        ProductPair memory prod3 = ProductPair(
            ProductInformation(42, "Ghost in the Shell (1995)", 100500 ether),
            Product("wioo wioo cyberpuk")
        );

        expectedProducts.push(prod0);
        expectedProducts.push(prod1);
        expectedProducts.push(prod2);
        expectedProducts.push(prod3);
    }
    

    function setUp() public {
        shop = new Shop();
        shop.transferOwnership(owner);

        vm.startPrank(owner);

        for (uint i = 0; i < expectedProducts.length; i++) {
            shop.addProduct(expectedProducts[i].product, expectedProducts[i].info);
        }

        vm.stopPrank();
    }


    // wrong addition and listing tests
    function test_PriceListCorrect() public {
        ProductInformation[] memory priceList = shop.getPriceList();

        for (uint i = 0; i < expectedProducts.length; i++) {
            assertEq(priceList[i].productId, expectedProducts[i].info.productId);
            assertEq(priceList[i].name, expectedProducts[i].info.name);
            assertEq(priceList[i].price, expectedProducts[i].info.price);
        }        
    }

    event NewProductAdded(uint256 indexed productId);

    function test_Add_EventTest() public {
        vm.startPrank(owner);
        
        ProductInformation memory info = ProductInformation(666, "Capital (Mihal Palych) (2010)", 0);
        Product memory prod = Product("kak tam s dengami");

        vm.expectEmit(address(shop));
        emit NewProductAdded(666);
        shop.addProduct(prod, info);

        vm.stopPrank();
    }

    function test_Add_DuplicateId() public {
        vm.expectRevert(
            abi.encodeWithSelector(Shop.ProductIdAlreadyExists.selector, 42) // глянуть что такое селектор
        );

        vm.startPrank(owner);

        ProductInformation memory info = ProductInformation(42, "The Matrix (1999)", 666);
        Product memory prod = Product("has already been");

        shop.addProduct(prod, info);

        vm.stopPrank();
    }

    // buying tests

    event ProductBoughtSuccesfully(uint256 indexed productId);

    function test_Buy_Successful() public {
        vm.deal(buyer, 6 ether);
        assertEq(buyer.balance, 6 ether);

        assertEq(address(shop).balance, 0 ether);

        vm.startPrank(buyer);
        vm.expectEmit(address(shop));
        emit ProductBoughtSuccesfully(7);
        Product memory product = shop.buyProduct{value: 5 ether}(7);
        vm.stopPrank();

        assertEq(address(shop).balance, 5 ether);
        assertEq(buyer.balance, 1 ether);
        assertEq(product.message, expectedProducts[1].product.message);
    }

    function test_Buy_PaidNotEnough() public {
        vm.expectRevert(
            abi.encodeWithSelector(Shop.IncorrectMoneyValue.selector, 100500 ether, 6 ether)
        );

        assertEq(address(shop).balance, 0 ether);

        vm.deal(buyer, 6 ether);
        assertEq(buyer.balance, 6 ether);

        vm.startPrank(buyer);
        shop.buyProduct{value: 6 ether}(42);
        vm.stopPrank();

        assertEq(address(shop).balance, 0 ether);
        assertEq(buyer.balanance, 6 ether);
    }

    function test_Buy_PaidTooMuch() public {
        vm.expectRevert(
            abi.encodeWithSelector(Shop.IncorrectMoneyValue.selector, 3 ether, 100500 ether)
        );

        assertEq(address(shop).balance, 0);

        vm.deal(buyer, 100501 ether);
        assertEq(buyer.balance, 100501 ether);

        vm.startPrank(buyer);
        shop.buyProduct{value: 100500 ether}(1);
        vm.stopPrank();

        assertEq(address(shop).balance, 0 ether);
        assertEq(buyer.balance, 100501 ether);
    }

    function test_Buy_NoSuchId() public {
        vm.expectRevert(
            abi.encodeWithSelector(Shop.NoProductWithSuchId.selector, 666)
        );

        assertEq(address(shop).balance, 0);

        vm.deal(buyer, 5 ether);
        assertEq(buyer.balance, 5 ether);

        vm.startPrank(buyer);
        shop.buyProduct{value: 5 ether}(666);
        vm.stopPrank();

        assertEq(address(shop).balance, 0 ether);
        assertEq(buyer.balance, 5 ether);
    }
}
