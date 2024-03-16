# Rust 语言

## 需要注意的知识点

### 所有权

- 一个对象任一时刻只能存在至多一个 mutable 引用，或者多个 immutable 引用。
  - 而且 immutable/mutable 引用是互斥的，不能同时存在。

### 生命周期

- 使用类似泛型的语法来标注生命周期 `<'a>`，不过大部分情况编译器都能自行处理，需要手动标注生命周期的
  情况有些少见。

### trait 与泛型

- 可以通过泛型选择性地实现 trait: `fn notify<T: Summary + Display>(item: &T) {...}`

  - 对于更复杂的情况，可以使用 `where` 语法提升可读性。

- 使用 Trait 来声明参数类型/返回值类
  型：`fn returns_summarizable(arg: impl Xxx) -> impl Summary {...}`
- Trait 对象（Trait Object）：`Box<dyn Xxx>`，还没学，不是很懂...

### 智能指针与并发安全

跟 C 语言一样，rust 默认在栈上分配空间，即使使用 reference 引用，也是一样的。

如果需要将数据存在堆上，就需要使用智能指针，如 `Box<T>`。

> C 语言中使用 `malloc/calloc` 分配堆内存，并且需要手动调用 `free` 释放内存，否则就会造成内存泄漏。

- `Box<T>`: 包装器，单纯需要将数据存在堆上时使用。
- `RefCell<T>`: 「内部可变」的 `Box<T>`，它在运行时检查「借用规则」，而不是在编译期。

  - 当您确定代码遵循借用规则但编译器无法理解和保证这一点时，可以使用 `RefCall<T>`.
  - 相对的，如果你的代码确实有问题，这会导致运行时错误！

- `Rc<T>` : 引用计数的智能指针。

  - 在各种树、图等数据结构中，一个对象（Node）很可能被多个其他对象所拥有，这种情况下，就需要使用到
    `Rc<T>`.

- `std::sync::mpsc::channel<T>`: 管道，类比 go 的 channel.
- `Arc<T>`: 并发安全的原子引用
- `Mutex<T>`: 互斥锁

- 通过实现 `Deref` trait，能像使用普通的 reference 一样地使用智能指针。
- `Drop` trait 会在对象被销毁前调用，通过它，用户可以实现自己的内存分配器。
- 可通过 `std::mem::drop` 函数提前 drop 掉对象（比如加并发锁时，就可能希望使用完毕立马 drop，不等到
  整个 block 结束）

- 智能指针的循环引用可能会导致内存泄漏。

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

## 宏 - macro

待续

## unsafe

待续

## async/await

- [async-book](https://rust-lang.github.io/async-book/)
