export async function placeOrder(db: Db, broker: Broker, order: Order) {
  await db.orders.insert(order);
  await broker.publish("orders", { type: "OrderPlaced", orderId: order.id });
}

export async function onOrderPlaced(msg: { orderId: string }, db: Db) {
  const order = await db.orders.get(msg.orderId);
  await db.loyalty.addPoints(order.customerId, order.total / 10);
}
