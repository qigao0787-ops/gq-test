# Java基础面试总结

> 整理自：Java 基础核心知识体系
> 适用：Java 后端面试（几乎每场必问）

---

## 一、数据类型与基础

### 1.1 基本数据类型

| 类型 | 字节 | 范围 | 默认值 |
|------|------|------|--------|
| byte | 1 | -128 ~ 127 | 0 |
| short | 2 | -32768 ~ 32767 | 0 |
| int | 4 | -2^31 ~ 2^31-1 | 0 |
| long | 8 | -2^63 ~ 2^63-1 | 0L |
| float | 4 | IEEE 754 | 0.0f |
| double | 8 | IEEE 754 | 0.0d |
| char | 2 | 0 ~ 65535 | '\u0000' |
| boolean | 1/4 | true/false | false |

### 1.2 自动装箱/拆箱

```java
// 自动装箱: 基本类型 → 包装类
Integer a = 100;  // Integer.valueOf(100)

// 自动拆箱: 包装类 → 基本类型
int b = a;        // a.intValue()

// ⚠️ 缓存陷阱
Integer x = 127, y = 127;
x == y  // true (缓存 -128~127)

Integer m = 128, n = 128;
m == n  // false (new 出来的对象)
```

### 1.3 String / StringBuilder / StringBuffer

| 类 | 可变性 | 线程安全 | 性能 |
|----|--------|---------|------|
| String | 不可变(final char[]) | 安全 | 拼接慢 |
| StringBuilder | 可变 | 不安全 | 快 |
| StringBuffer | 可变 | 安全(synchronized) | 较慢 |

```java
// String 不可变原因
// 1. final 修饰类，不可继承
// 2. char[] 数组 private final（JDK9 改为 byte[]）
// 3. 没有提供修改内部数组的方法

// String 常量池
String s1 = "abc";           // 常量池
String s2 = new String("abc"); // 堆
s1 == s2       // false
s1.equals(s2)  // true
s1 == s2.intern()  // true (intern 返回常量池引用)
```

---

## 二、面向对象

### 2.1 三大特性

| 特性 | 说明 | 关键字/机制 |
|------|------|------------|
| 封装 | 隐藏内部实现 | private/getter/setter |
| 继承 | 代码复用 | extends/implements |
| 多态 | 同一接口不同实现 | 重写/向上转型/动态绑定 |

### 2.2 重载 vs 重写

| 维度 | 重载(Overload) | 重写(Override) |
|------|----------------|----------------|
| 位置 | 同一个类 | 子类 |
| 方法名 | 相同 | 相同 |
| 参数 | 必须不同 | 必须相同 |
| 返回值 | 无要求 | 相同或协变 |
| 访问权限 | 无要求 | ≥ 父类 |
| 异常 | 无要求 | ≤ 父类 |

### 2.3 抽象类 vs 接口

| 维度 | 抽象类 | 接口(JDK8+) |
|------|--------|-------------|
| 关键字 | abstract class | interface |
| 构造器 | 有 | 无 |
| 成员变量 | 任意 | public static final |
| 方法 | 抽象+具体 | default/static/抽象 |
| 继承 | 单继承 | 多实现 |
| 设计语义 | is-a | can-do |

### 2.4 == vs equals vs hashCode

```java
// == : 比较引用地址（基本类型比较值）
// equals : 默认同 ==，可重写比较内容
// hashCode : 对象的哈希值

// 规则：
// 1. equals 相等 → hashCode 必须相等
// 2. hashCode 相等 → equals 不一定相等
// 3. 重写 equals 必须重写 hashCode (HashMap 依赖)
```

---

## 三、集合框架

### 3.1 集合体系总览

```
┌─────────────────────────────────────────────────────┐
│                Collection                           │
├──────────────────┬──────────────────────────────────┤
│      List        │          Set                     │
│  ├─ ArrayList    │  ├─ HashSet (HashMap)            │
│  ├─ LinkedList   │  ├─ LinkedHashSet                │
│  └─ Vector       │  └─ TreeSet (红黑树)             │
├──────────────────┴──────────────────────────────────┤
│                  Map                                │
│  ├─ HashMap                                        │
│  ├─ LinkedHashMap                                  │
│  ├─ TreeMap (红黑树)                                │
│  ├─ ConcurrentHashMap                              │
│  └─ Hashtable (过时)                                │
└─────────────────────────────────────────────────────┘
```

### 3.2 ArrayList vs LinkedList

| 维度 | ArrayList | LinkedList |
|------|-----------|------------|
| 底层 | Object[] 数组 | 双向链表 |
| 随机访问 | O(1) | O(n) |
| 头部插入 | O(n) | O(1) |
| 尾部插入 | O(1) 均摊 | O(1) |
| 内存 | 连续，缓存友好 | 不连续，每个节点额外指针 |
| 扩容 | 1.5倍 | 无需扩容 |

### 3.3 HashMap (JDK8) ★★★★★

```
┌─────────────────────────────────────────────────────┐
│            HashMap 底层结构 (JDK8)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  数组 (Node[]) + 链表 + 红黑树                       │
│                                                     │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┐                │
│  │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │  ... (16)    │
│  └─┬─┴───┴─┬─┴───┴───┴─┬─┴───┴───┘                │
│    │       │           │                           │
│    ▼       ▼           ▼                           │
│  [A]→[B] [C]→[D]→[E] [F]→...→[8个]→转红黑树       │
│                                                     │
│  默认容量: 16                                       │
│  负载因子: 0.75                                     │
│  树化阈值: 链表长度 ≥ 8 且数组 ≥ 64                  │
│  退化阈值: 红黑树节点 ≤ 6 退化为链表                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**put 流程：**
```java
// 1. hash(key): (h = key.hashCode()) ^ (h >>> 16)  扰动函数
// 2. 定位桶: (n-1) & hash
// 3. 桶为空 → 直接放入
// 4. 桶不为空:
//    - key 相同(equals) → 覆盖 value
//    - 链表 → 尾插法，长度≥8 且数组≥64 → 树化
//    - 红黑树 → 树节点插入
// 5. 判断 size > threshold → resize() 扩容2倍
```

**扩容机制：**
```java
// 新容量 = 旧容量 << 1 (2倍)
// 新阈值 = 新容量 * 负载因子
// 元素重新分布: hash & oldCap == 0 ? 原位 : 原位+oldCap
// JDK8 优化: 不需要重新 hash，只看高一位是0还是1
```

### 3.4 ConcurrentHashMap ★★★★★

| 维度 | JDK7 | JDK8 |
|------|-------|------|
| 结构 | Segment[] + HashEntry[] | Node[] + 链表/红黑树 |
| 锁粒度 | 分段锁(Segment extends ReentrantLock) | CAS + synchronized(节点头) |
| 并发度 | 默认16个Segment | 理论无限(桶级别) |
| size() | 多次不加锁统计，不一致则全锁 | baseCount + CounterCell[] |

```java
// JDK8 put 流程
// 1. key 的 hash 值 spread
// 2. 如果桶为空 → CAS 放入
// 3. 如果正在扩容(MOVED) → 帮助扩容
// 4. 桶不为空 → synchronized(头节点) {链表/红黑树操作}
// 5. 链表长度≥8 → 树化
// 6. addCount → 判断是否扩容
```

### 3.5 HashMap 常见面试题

| 问题 | 答案 |
|------|------|
| 为什么容量是2的幂 | (n-1)&hash 等价于 hash%n，位运算更快 |
| 为什么负载因子是0.75 | 时间和空间的折中(泊松分布) |
| 为什么链表转红黑树阈值是8 | 泊松分布下链表长度达到8的概率极低(0.00000006) |
| HashMap 线程不安全表现 | JDK7 死循环(头插法)，JDK8 数据覆盖 |
| key 可以为 null 吗 | HashMap 可以(放在0号桶)，ConcurrentHashMap 不可以 |

---

## 四、异常体系

```
Throwable
├── Error (不可恢复)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── NoClassDefFoundError
└── Exception
    ├── RuntimeException (非受检)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   └── IllegalArgumentException
    └── 受检异常 (必须 try-catch 或 throws)
        ├── IOException
        ├── SQLException
        └── ClassNotFoundException
```

---

## 五、泛型

### 5.1 类型擦除

```java
// 编译后泛型信息被擦除
List<String> list = new ArrayList<>();
// 编译后: List list = new ArrayList();

// 不能做的事:
// new T()          ← 擦除后不知道T是什么
// instanceof T     ← 同上
// new T[]          ← 同上
// 静态字段/方法中使用类泛型
```

### 5.2 通配符

| 通配符 | 含义 | 读写 |
|--------|------|------|
| `<?>` | 任意类型 | 只读 |
| `<? extends T>` | T 或 T 的子类(上界) | 只读(生产者) |
| `<? super T>` | T 或 T 的父类(下界) | 只写(消费者) |

> PECS 原则: Producer Extends, Consumer Super

---

## 六、反射与动态代理

### 6.1 反射

```java
// 获取 Class 对象
Class<?> clazz = Class.forName("com.example.User");
Class<?> clazz = User.class;
Class<?> clazz = user.getClass();

// 创建实例
Object obj = clazz.getDeclaredConstructor().newInstance();

// 获取/调用方法
Method method = clazz.getDeclaredMethod("setName", String.class);
method.setAccessible(true);  // 破解私有
method.invoke(obj, "Tom");
```

### 6.2 动态代理

| 维度 | JDK 动态代理 | CGLIB |
|------|-------------|-------|
| 原理 | 反射 + Proxy.newProxyInstance | ASM 字节码生成子类 |
| 要求 | 目标类必须实现接口 | 目标类不能是 final |
| 性能 | JDK8+ 已优化，差距不大 | 生成的字节码直接调用 |
| Spring AOP | 有接口默认用 JDK | 无接口用 CGLIB |

```java
// JDK 动态代理
Object proxy = Proxy.newProxyInstance(
    target.getClass().getClassLoader(),
    target.getClass().getInterfaces(),
    (proxy1, method, args) -> {
        System.out.println("before");
        Object result = method.invoke(target, args);
        System.out.println("after");
        return result;
    }
);
```

---

## 七、Java IO

### 7.1 IO 模型

| 模型 | 说明 | Java 实现 |
|------|------|----------|
| BIO | 同步阻塞 | InputStream/OutputStream |
| NIO | 同步非阻塞 | Channel + Buffer + Selector |
| AIO | 异步非阻塞 | AsynchronousChannel |

### 7.2 NIO 三大组件

```
┌─────────────────────────────────────────────────────┐
│                NIO 核心                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Channel (通道) - 双向数据管道                       │
│    FileChannel / SocketChannel / ServerSocketChannel │
│                                                     │
│  Buffer (缓冲区) - 数据容器                         │
│    ByteBuffer / CharBuffer                          │
│    position / limit / capacity                      │
│                                                     │
│  Selector (多路复用器) - 一个线程管理多个 Channel    │
│    select() → 获取就绪的 Channel                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 八、JDK 新特性

### 8.1 JDK 8 核心特性

| 特性 | 说明 |
|------|------|
| Lambda 表达式 | `(x, y) -> x + y` |
| Stream API | 集合的函数式操作(filter/map/reduce) |
| Optional | 优雅处理 null |
| 接口 default 方法 | 接口可以有默认实现 |
| 方法引用 | `System.out::println` |
| 新日期 API | LocalDate/LocalDateTime/Duration |
| CompletableFuture | 异步编程 |

### 8.2 Stream 常用操作

```java
List<String> result = list.stream()
    .filter(s -> s.length() > 3)       // 过滤
    .map(String::toUpperCase)          // 转换
    .sorted()                          // 排序
    .distinct()                        // 去重
    .limit(10)                         // 取前10
    .collect(Collectors.toList());     // 收集

// 分组
Map<String, List<User>> grouped = users.stream()
    .collect(Collectors.groupingBy(User::getDept));

// 聚合
int total = orders.stream()
    .mapToInt(Order::getAmount)
    .sum();
```

### 8.3 JDK 11+ 重要特性

| JDK | 特性 |
|-----|------|
| 11 | var 局部变量推断 / HttpClient / String 新方法 |
| 14 | Records (数据类) / Switch 表达式 |
| 15 | 密封类(sealed class) / 文本块 |
| 17 | Pattern Matching / sealed 正式版 (LTS) |
| 21 | 虚拟线程(Virtual Threads) / Record Patterns (LTS) |

### 8.4 虚拟线程 (JDK 21) ★

```java
// 传统线程: 1个线程 = 1个OS线程 (重量级，约1MB栈)
// 虚拟线程: 百万级轻量线程，由JVM调度

// 创建虚拟线程
Thread.startVirtualThread(() -> {
    // 任务
});

// 使用 ExecutorService
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            Thread.sleep(1000);
            return "done";
        });
    }
}

// 适用场景: IO 密集型 (HTTP调用/DB查询)
// 不适用: CPU 密集型计算
```

---

## 九、面试高频问题

| 序号 | 问题 | 关键点 |
|------|------|--------|
| 1 | HashMap 底层原理 | 数组+链表+红黑树/扩容/hash扰动 |
| 2 | HashMap vs ConcurrentHashMap | 分段锁→CAS+synchronized |
| 3 | ArrayList vs LinkedList | 数组vs链表/随机访问vs插入 |
| 4 | String 为什么不可变 | final class + private final char[] |
| 5 | == 和 equals 区别 | 引用vs内容/hashCode契约 |
| 6 | 接口和抽象类的区别 | 多实现vs单继承/is-a vs can-do |
| 7 | 反射的应用场景 | 框架/AOP/序列化 |
| 8 | JDK 动态代理 vs CGLIB | 接口vs子类/Proxy vs ASM |
| 9 | Stream 的 map 和 flatMap | 一对一 vs 一对多展平 |
| 10 | 虚拟线程和平台线程区别 | 轻量/JVM调度/IO密集适用 |

---

*整理完成，祝面试顺利！*
