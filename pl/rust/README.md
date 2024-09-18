# Rust 语言

> 个人笔记，不保证准确性。

学习路线：

1. 阅读 The Book
2. 做完 Rustlings
3. TODO

## 需要注意的知识点

### 所有权

- 一个对象任一时刻只能存在至多一个 mutable 引用，或者多个 immutable 引用。
  - immutable/mutable 引用是互斥的，不能同时存在。

### 生命周期

- 使用类似泛型的语法来标注生命周期 `<'a>`，不过大部分情况编译器都能自行处理，需要手动标注生命周期的
  情况有些少见。

### trait 与泛型

- 可以通过泛型选择性地实现 trait: `fn notify<T: Summary + Display>(item: &T) {...}`
  - 对于更复杂的情况，可以使用 `where` 语法提升可读性。
- 使用 Trait 来声明参数类型/返回值类
  型：`fn returns_summarizable(arg: impl Xxx) -> impl Summary {...}`
- Trait 对象（Trait Object）：`Box<dyn Xxx>`，可类比 Go 的接口对象。
  - 即在不关注对象的具体类型，而只关注它是否实现了某个 trait 时，可以将它转换成一个 trait 对象（Go
    的接口对象）。
- trait 有些类似 Go 的 interface，区别是它可以有默认实现（这方面更类似 Java）。

### 迭代器

- Rust 的迭代器是零开销抽象，性能甚至比 loop 循环还稍微好一点，代码也比循环更简洁易懂，强烈建议使
  用。

### 模式匹配

模式匹配中的两个关键概念：

- refutable： 可反驳的，即可能失败的模式匹配。
- irrefutable：不可反驳的，即不可能失败的模式匹配。

以上概念可能会在模式匹配的报错中出现，这表示你需要切换到 `let`/`if let`/`while let` 等其他合适的匹配
语句。

Rust 的模式匹配非常强大，支持很多复杂的条件匹配、解构、绑定等操作，详见：

https://doc.rust-lang.org/book/ch18-03-pattern-syntax.html

## 错误处理

- https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/boxing_errors.html

- 随意啦，能跑就行：https://github.com/dtolnay/anyhow
- 还是严谨一点，要给人看的：https://github.com/dtolnay/thiserror

## 类型转换 - conversion

还需要研究

- `as_ref`/`as_mut`: 几乎没有性能损耗的类型转换
- `from`/`into`: 所有实现了 `From` Trait 的类型，都会自动实现 `Into`
- `try_into`/`try_from`/`from_str`: 这三个都是返回 Result 类型的类型转换方法。
  - 自己实现时，都需要返回 `Result<Self, Self::Error>` 类型的值，这个对初学者而言有点难度。
- `into_iter`/`iter`/`iter_mut`

## 函数式编程

rust 的高阶函数 + 链式语法超级好用！

- `map`/`fold`/`filter`/`filter_map`/`partition`
- `collect`/`reduct`/`count`/`sum`

## 智能指针与并发安全

跟 C 语言一样，rust 默认在栈上分配空间，即使使用 reference 引用，也是一样的。

如果需要将数据存在堆上，就需要使用智能指针，如 `Box<T>`。

> C 语言中使用 `malloc/calloc` 分配堆内存，并且需要手动调用 `free` 释放内存，否则就会造成内存泄漏。

- `Box<T>`: 包装器，单纯需要将数据存在堆上时使用，主要应用场景：
  - 在实现递归数据结构时（如链表），因为递归数据结构的大小无法在编译时确定（譬如链表的大小受元素个数
    影响，但无法在编译期确定元素个数），所以只能将它们放在堆上。
    - 回想下，C 语言中也需要使用指针才能实现链表，添加节点时也需要用 `malloc` 分配堆内存，`Box` 就干
      了类似的事。
  - 你希望将 ownership 传递给别人，但又不希望 copy 整个数据，这时就可以将它包装一下，这样就只有外层
    的包装器会被复制，性能更好。
  - 当你只关心一个对象是否实现了某个 trait 时，可以使用 `Box<dyn Trait>`，这也就是所谓的「trait
    Object」。
  - `Box<T>` 与 `&T` 的区别在于，`Box<T>` 拥有被引用的对象，而 `&T` 只是一个借用。
- 通过实现 `Deref` trait，能像使用普通的 reference 一样地使用智能指针。

  - From &T to &U when `T: Deref<Target=U>`
  - From &mut T to &mut U when `T: DerefMut<Target=U>`
  - From &mut T to &U when `T: Deref<Target=U>`
    - 注意，只有 mut 引用才能转换成 immutable 引用，反之不行。权限只能缩小，不能扩大。或者说皇帝能微
      服私访，但小卒不能冒充皇帝。

- `Drop` trait 会在对象被销毁前调用，通过它，用户可以实现自己的内存分配器。
  - 这确保了内存、文件句柄等资源能够被及时释放，避免内存泄漏等问题。
- 可通过 `std::mem::drop` 函数提前 drop 掉对象（比如加并发锁时，就可能希望使用完毕立马 drop，不等到
  整个 block 结束）
- `Rc<T>` : 引用计数（reference counting）的智能指针。

  - 在各种树、图等数据结构中，一个对象（Node）很可能被多个其他对象所拥有（Rust 的对象默认只能有一个
    Owner），这种情况下，就需要使用到 `Rc<T>`.

- `RefCell<T>`: 「内部可变（Interior mutability）」的 `Box<T>`，主要用于实现对象的多个可变引用。它在
  运行时检查「借用规则」，而不是在编译期.

  - 「内部可变性」即，即使对象本身是不可变的，但它内部的数据却是可变的。譬如你可以使用
    `let mut s = s;` 将一个 `&String` 转换成 `&mut String`，这样就可以使用 `push_str` 等方法了。
  - 在编译期检查借用规则太严格了，它使某些实际上内存安全的代码 Pattern 无法通过编译，而 `RefCell<T>`
    使我们能够绕过这些限制。
  - 相对的，如果你的代码确实有问题，`RefCell<T>` 会在运行时检测到借用规则被违反，并导致程序 panic.
  - 同时这会带来一定的性能损失吗？
    - 既然如此？为什么要在运行时检查借用规则？不检查不就没性能损失了？因为不检查就可能会出现难以排查
      的内存泄漏、数据竞争等问题，~~这是 `unsafe` 的范畴了，只有在 `unsafe` 块中才能关闭借用检查~~（貌似 unsafe 也不能关掉它...）。

- 智能指针的循环引用可能会导致内存泄漏。Rust 的各种规则只是极大降低了内存泄漏的可能，但并不能完全杜
  绝。

## 并发编程

Rust 的 Ownership 与 Borrowing 机制不仅降低了内存泄漏的可能，还能有效避免并发编程中的数据竞争问题。
许多 C 语言中的并发问题在 Rust 中都是编译期错误。

Rust 的线程实现使用 1:1 模型，即一个 Rust 线程对应一个 OS 线程。

> 其他语言中，Go 的协程使用 M:N 模型，即 Go 协程与 OS 线程是多对多的关系。Java 与 Rust 一样，也是
> 1:1 模型。

- `std::thread::spawn` 常与 `move` 一起使用，将 closure 的数据所有权转移给新线程，否则借用检查会报
  错。
- `std::sync::mpsc::channel<T>` 用于线程间通信，类似 Go 的 channel.
- 共享内存是另一种并发模型
  - 在 Go 等语言中，共享内存很容易出现数据竞争问题，所以 Go 强烈推荐 channel 模型，避免使用共享内
    存。但 Rust 的 Ownership 与 Borrowing 机制，使得共享内存模型更加安全，因此 Rust 的共享内存模型也
    值得一试。
- `Mutex<T>`: 互斥锁，也可以理解为 `RefCell<T>` 的并发安全版本。
  - 因为通常需要多处引用，常以 `Rc::new(Mutex::new(0))` 的形式使用。
  - 它与 `RefCell<T>` 都是「内部可变性」的 `Box<T>` 智能指针，所有引用都可以调用 `lock` 来尝试获取互
    斥锁。
- `Arc<T>`: 并发安全的原子引用，即 `Rc<T>` 的并发安全版本。

- 两个并发安全的 Traits
  - `Send`: 实现了这个 Trait 的数据类型可安全地跨线程传递
  - `Sync`: 实现了这个 Trait 的数据类型可安全地在多线程中共享
- 上述两个 Traits 甚至没有任何方法，只是一个标记。
- 手动实现 `Send`/`Sync` Trait 可能会导致并发问题，因此必须使用 `unsafe` 关键字。

不像 Go/C 等语言中，你可以在并发编程中使用普通的非线程安全的数据结构，而在 Rust 中，你如果在并发编程
中使用 `Box<T>`/`Rc<T>` 等数据结构，编译器会直接报错，告诉你它们未实现 `Send`/`Sync` trait，即不是线
程安全的。

## unsafe

Unsafe 的 5 项特殊能力：

- Dereference a raw pointer
- Call an unsafe function or method
- Access or modify a mutable static variable
- Implement an unsafe trait
- Access fields of a union

> 注意：unsafe 代码块仍然会被借用检查器与其他 Rust 安全策略检查，unsafe 只是使你可以使用上述 5 项特
> 殊能力，但 unsafe 代码仍旧需要遵守 Rust 的安全规则。

最佳实践：

- 尽可能只在必要的时候使用 unsafe，使 unsafe 代码尽可能地少。在排查内存安全问题时你会感谢这个决定。

## 宏 - macro

待续


## async/await

- [async-book](https://rust-lang.github.io/async-book/)
