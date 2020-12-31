Scrapy 中常用的数据提取方式有三种：Css 选择器、XPath、正则表达式。

## Css 选择器
Web 中的 [Css 选择器](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Selectors)，本来是用于实现在特定 DOM 元素上应用花括号内的样式这样一个功能的。
在爬虫中，我们可以用它来选择提取出需要的内容。Css 有非常丰富的功能，因为我们只用它提取数据，我们只会用到 Css 的选择器。

1. 标签选择器：直接写标签名，比如`title`就表示选择 title 这个标签。
2. 类选择器：以小数点开头，比如`.nav`就表示选择所有 class 属性为`nav`的 DOM 元素。
3. ID 选择器：以 # 开头，比如`#content`就表示选择 id 属性为`content`的 DOM 元素。（跟据 css 规范，id 属性值应该是唯一的，不能存在其他具有相同 id 的元素）
3. [属性选择器](https://developer.mozilla.org/en-US/docs/Web/CSS/Attribute_selectors)：写在[]括号内，如`a[href="https://example.org"]`
4. 伪元素选择器：伪元素选择器来自Css3规范，使用两个冒号引导。最常用的应该是`title::text`这个伪元素。（不过 css3 规范里好像没有 text 伪元素）
5. 关系选择器：[基于关系的选择器-MDN](https://developer.mozilla.org/zh-CN/docs/Web/Guide/CSS/Getting_started/Selectors#%E8%B5%84%E6%96%99_%E5%9F%BA%E4%BA%8E%E5%85%B3%E7%B3%BB%E7%9A%84%E9%80%89%E6%8B%A9%E5%99%A8)

## XPath

直接看阮老师的吧：[xpath路径表达式笔记 - 阮一峰](http://www.ruanyifeng.com/blog/2009/07/xpath_path_expressions.html)

## 正则

正则我倒是很熟悉，以前搞小鹤音形码表搞熟练了，就不介绍了，给几个教程和测试网站：

- [正则表达式30分钟入门教程](https://deerchao.cn/tutorials/regex/regex.htm)
- [RegExr - Learn, Build & Test RegExr](https://regexr.com/)

## 参考

- [CSS选择器笔记 - 阮一峰](http://www.ruanyifeng.com/blog/2009/03/css_selectors.html)
- [xpath路径表达式笔记 - 阮一峰](http://www.ruanyifeng.com/blog/2009/07/xpath_path_expressions.html)