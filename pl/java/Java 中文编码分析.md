### 一、charAt 与 codePonitAt

我们知道 Java 内部使用的是 utf-16 作为它的 char、String 的字符编码方式，这里我们叫它内部字符集。而 utf-16 是变长编码，一个字符的编码被称为一个 code point，它可能是 16 位 —— 一个 code unit，也可能是 32 位 —— 两个 code unit。
Java 的 char 类型长度为二字节，它对应的是 code unit。换句话说，一个字符的编码，可能需要用两个 char 来存储。

作为一个输入法爱好者，我偶尔会编程处理一些生僻字。其中有些生僻字大概是后来才加入 unicode 字符集里的，直接用 charAt 方法读取它们，会得到一堆问号。原因很清楚 —— 因为这些字符（eg. "𫖯"）是用两个 code unit，也就是两个 char 表示的。charAt 找不到对应的编码，就会将这些 char 输出成「?」。
```java
//示例
public class Test {
    public static void main(String[] args){
        String s = "𫖯";
        System.out.println(s.length());   //输出：2
        System.out.println(s.charAt(0));  //输出：?
        System.out.println(s.charAt(1));  //输出：?
    }
}

```
因此，涉及到中文，一定要使用 String 而不是 char，并且使用 codePoint 相关方法来处理它。否则的话，如果用户使用了生僻字，很可能就会得到不想要的结果。


下面是一个使用 codePoint 遍历一个字符串的示例，需要注意的是，codePoint 是 int 类型的（因为 char 不足以保存一个 codepoint），因此需要做些额外的转换：
```java
public class Test {
    public static void main(String[] args){

        String s = "赵孟𫖯孟";
        for (int i = 0; i < s.codePointCount(0,s.length()); i++) {
            System.out.println(
                    new String(Character.toChars(s.codePointAt(i))));
                    // 这里的轨迹是：类型为 int 的 codepoint -> char数组 -> String 
        }

    }
}

/* 结果：
        赵
        孟
        𫖯
        ?
*/
```
问题来了，「𫖯」这个字是正常地输出了，可最后的「孟」却变成了黑人问号。。
原因就在于 codepointAt(i) 是以 char 偏移量索引的。。所以只是这样输出也是不行的。。

正确的遍历姿势是这样的
```java
final int length = s.length();
for (int offset = 0; offset < length; ) {
   final int codepoint = s.codePointAt(offset);

   System.out.println(new String(Character.toChars(codepoint)));

   offset += Character.charCount(codepoint);
}
```
这个代码保持了一个变量offset, 来指示下一个 codepoint 的偏移量。最后那一句在处理完毕后，更新这个偏移量

而 Java 8 添加了 [`CharSequence#codePoints`](http://docs.oracle.com/javase/8/docs/api/java/lang/CharSequence.html#codePoints--)， 该方法返回一个 `IntStream`，该流包含所有的 codepoint。可以直接通过 forEach 方法来遍历他。
```java
string.codePoints().forEach(
        c -> System.out.println(new String(Character.toChars(c)));
);
```
或者用循环
```java
for(int c : string.codePoints().toArray()){
    System.out.println(new String(Character.toChars(c)));
}
```

### 二、内部字符集与输出字符集（内码与外码）
现在我们知道了中文字符在 java 内部可能会保存成两个 char，可还有个问题：如果我把一个字符输出到某个流，它还会是两个 char，也就是 4 字节么？
回想一下，Java io 有字符流，字符流使用 jvm 默认的字符集输出，而若要指定字符集，可使用转换流。
因此，一个中文字符，在内部是使用 utf-16 表示，可输出就不一定了。
来看个示例：
```java
import java.io.UnsupportedEncodingException;

public class Test {
    public static void main(String[] args)
            throws UnsupportedEncodingException {

        String s = "中";   //𫖯
        System.out.println(s + ": chars: " + s.length());
        System.out.println(s + ": utf-8 bytes:" + s.getBytes("utf-8").length);
        System.out.println(s + ": unicode bytes: " + s.getBytes("unicode").length);
        System.out.println(s + ": utf-16 bytes: " + s.getBytes("utf-16").length);
    }
}
```

输出为：
```
中: chars: 1      // 2 bytes 
中: utf-8 bytes:3
中: unicode bytes: 4
中: utf-16 bytes: 4


𫖯: chars: 2       // 4 bytes
𫖯: utf-8 bytes:4
𫖯: unicode bytes: 6
𫖯: utf-16 bytes: 6
```

一个「中」字，内部存储只用了一个 char，也就是 2 个字节。可转换成 utf-8 编码后，却用了 3 个字节。怎么会不一样呢，是不是程序出了问题？
当然不是程序的问题，这是内码(utf-16)转换成外码(utf-8)，字符集发生了改变，所使用的字节数自然也可能会改变。（尤其这俩字符集还都是变长编码）

### 三、utf-16、utf-16le、utf-16be、bom
不知道在刚刚的示例中，你有没有发现问题：同是 utf-16，为何「中」和「𫖯」的 `s.getBytes("utf-16").length` 比  `s.length` 要多个 2？开头就说了 String 也是 `utf-16` 编码的，这两个数应该相等才对不是吗？
原因在于，utf-16 以 16 位为单位表示数据，而计算机是以字节为基本单位来存储/读取数据的。因此一个 utf-16 的 code unit 会被存储为两个字节，需要明确指明这两个字节的先后顺序，计算机才能正确地找出它对应的字符。而 utf-16 本身并没有指定这些，所以它会在字符串开头插入一个两字节的数据，来存储这些信息（大端还是小端）。这两个字节被称为BOM（Byte Order Mark）。刚刚发现的多出的两字节就是这么来的。
如果你指定编码为 utf-16le 或 utf-16be，就不会有这个 BOM 的存在了。这时就需要你自己记住该文件的大小端。。

### 四、更多：utf-8 unicode
1. 在 windows 中，utf-8 格式的文件也可能会带有 BOM，但 utf-8 的基本单位本来就是一个字节，因此它不需要 BOM 来表示 所谓大小端。这个 BOM 一般是用来表示该文件是一个 utf-8 文件。不过 linux 系统则对这种带 BOM 的文件不太友好。不般不建议加。。（虽如此说，上面的测试中，utf-8 的数据应该是没加 bom 的结果）
2. unicode字符集UCS（Unicode Character Set） 就是一张包含全世界所有文字的一个编码表，但是 UCS 太占内存了，所以实际使用基本都是使用它的其他变体。一般来说，指定字符集时使用的 unicode 基本等同于 utf-16.（所以你会发现第二节演示的小程序里，utf-16 和 unicode 得出的结果是一样的。）


### 四、与 Python3 对比
python3 在字符串表示上，做了大刀阔斧的改革，python3 的 len(str) 得到的就是 unicode 字符数，因此程序员完全不需要去考虑字符的底层表示的问题。（实际上其内部表示也可能随着更新而变化）带 BOM 的 utf-8 也可通过指定字符集为 `utf-8-sig` 解决。若需要做字符集层面处理，需要 encode 为特定字符集的 byte 类型。
>Encoding pertains mostly to files and transfers. Once
loaded into a Python string, text in memory has no notion of an “encoding,” and is
simply a sequence of Unicode characters (a.k.a. code points) stored generically.
                                                                                    -- Learning Python 5th

>P.S. Python2 存在和 Java 相同的问题

### 参考
- [java 语言中的一个字符占几个字节？ - RednaxelaFX - 知乎](https://www.zhihu.com/question/27562173/answer/37188642)
- [How can I iterate through the unicode codepoints of a Java String?](https://stackoverflow.com/questions/1527856/how-can-i-iterate-through-the-unicode-codepoints-of-a-java-string)
- [彻底搞懂字符编码(unicode,mbcs,utf-8,utf-16,utf-32,big endian,little endian...)](http://blog.csdn.net/softman11/article/details/6124345)
- [Java_字符编码](http://blog.csdn.net/tianjf0514/article/details/7854624)


本文允许转载，但要求附上源链接：[Java 中文编码分析](http://www.cnblogs.com/kirito-c/p/8544408.html)