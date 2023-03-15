# VSCode C/C++ 开发环境搭建

VSCode 的 C/C++ 插件功能虽然全但是速度比较拉，跳转个定义卡半天，而且还经常给出一堆莫名的引用，体验极其糟糕。而 llvm 项目推出的 clangd 应用广泛，体验丝滑，直接吊打 VSCode C/C++ 插件（举个例子 Clion 就是基于 clangd 开发的）。

这里就简单介绍下如何用 clangd 搭建开发环境，其实挺简单的。

需要的工具：

- VSCode 插件
  - clangd
  - codelldb
- 依赖（直接包管理器安装就行）
  - clang
  - cmake
  - lldb
  - clangd: 这个组件可以使用系统包管理器安装，也可以由 vscode 插件自行下载安装。

环境装好后还需要一点点工作—— clang 借助 `compile_commands.json` 进行语法提示，但这个配置可不是让你手写的，有很多工具可以自动生成它：

1. 对于使用 make 的项目，可以直接使用 [rizsotto/Bear](https://github.com/rizsotto/Bear) 自动生成此文件
2. 对于使用 cmake 的项目就更简单了，cmake 原生就支持，只需要在根目录的配置文件中添加 `set(CMAKE_EXPORT_COMPILE_COMMANDS True)`
3. 其他工具的配置方法请自行搜索。

对于自定义程度较高的大型项目就得具体情况具体分析了，比如 Linux 内核其实本身就提供了生成 `compile_commands.json` 的脚本：[scripts/clang-tools/gen_compile_commands.py](https://github.com/torvalds/linux/blob/master/scripts/clang-tools/gen_compile_commands.py)

## GCC / Clang 常见参数解释

主要摘抄自 [man gcc](https://man7.org/linux/man-pages/man1/gcc.1.html)，用做日常参考:


```shell
# debug 或学习编译流程时常用的选项
    Useful
       -c  Compile or assemble the source files, but do not link.  The
           linking stage simply is not done.  The ultimate output is in
           the form of an object file for each source file.

           By default, the object file name for a source file is made by
           replacing the suffix .c, .i, .s, etc., with .o.

           Unrecognized input files, not requiring compilation or
           assembly, are ignored.

       -S  Stop after the stage of compilation proper; do not assemble.
           The output is in the form of an assembler code file for each
           non-assembler input file specified.

           By default, the assembler file name for a source file is made
           by replacing the suffix .c, .i, etc., with .s.

           Input files that don't require compilation are ignored.

       -E  Stop after the preprocessing stage; do not run the compiler
           proper.  The output is in the form of preprocessed source
           code, which is sent to the standard output.

           Input files that don't require preprocessing are ignored.
       -Wall
           This enables all the warnings about constructions that some
           users consider questionable, and that are easy to avoid (or
           modify to prevent the warning), even in conjunction with
           macros.  This also enables some language-specific warnings
           described in C++ Dialect Options and Objective-C and
           Objective-C++ Dialect Options.

# 预处理选项：
   Preprocessor Options
       -D<macroname>=<value>
              Adds an implicit #define into the predefines buffer which is read before the source file is preprocessed.

       -U<macroname>
              Adds an implicit #undef into the predefines buffer which is read before the source file is preprocessed.

       -include <filename>
              Adds an implicit #include into the predefines buffer which is read before the source file is preprocessed.

       -I<directory>
              Add the specified directory to the search path for include files.

       -F<directory>
              Add the specified directory to the search path for framework include files.

       -nostdinc
              Do not search the standard system directories or compiler builtin directories for include files.

       -nostdlibinc
              Do not search the standard system directories for include files, but do search compiler builtin include directories.

       -nobuiltininc
              Do not search clang's builtin directory for include files.


# 文件夹选项
   Options for Directory Search
       These options specify directories to search for header files, for
       libraries and for parts of the compiler:

       -I dir
       -iquote dir
       -isystem dir
       -idirafter dir
           Add the directory dir to the list of directories to be
           searched for header files during preprocessing.  If dir
           begins with = or $SYSROOT, then the = or $SYSROOT is replaced
           by the sysroot prefix; see --sysroot and -isysroot.

           Directories specified with -iquote apply only to the quote
           form of the directive, "#include "file"".  Directories
           specified with -I, -isystem, or -idirafter apply to lookup
           for both the "#include "file"" and "#include <file>"
           directives.

           You can specify any number or combination of these options on
           the command line to search for header files in several
           directories.  The lookup order is as follows:

           1.  For the quote form of the include directive, the
               directory of the current file is searched first.

           2.  For the quote form of the include directive, the
               directories specified by -iquote options are searched in
               left-to-right order, as they appear on the command line.

           3.  Directories specified with -I options are scanned in
               left-to-right order.

           4.  Directories specified with -isystem options are scanned
               in left-to-right order.

           5.  Standard system directories are scanned.

           6.  Directories specified with -idirafter options are scanned
               in left-to-right order.

           You can use -I to override a system header file, substituting
           your own version, since these directories are searched before
           the standard system header file directories.  However, you
           should not use this option to add directories that contain
           vendor-supplied system header files; use -isystem for that.

           The -isystem and -idirafter options also mark the directory
           as a system directory, so that it gets the same special
           treatment that is applied to the standard system directories.

           If a standard system include directory, or a directory
           specified with -isystem, is also specified with -I, the -I
           option is ignored.  The directory is still searched but as a
           system directory at its normal position in the system include
           chain.  This is to ensure that GCC's procedure to fix buggy
           system headers and the ordering for the "#include_next"
           directive are not inadvertently changed.  If you really need
           to change the search order for system directories, use the
           -nostdinc and/or -isystem options.

       -I- Split the include path.  This option has been deprecated.
           Please use -iquote instead for -I directories before the -I-
           and remove the -I- option.

           Any directories specified with -I options before -I- are
           searched only for headers requested with "#include "file"";
           they are not searched for "#include <file>".  If additional
           directories are specified with -I options after the -I-,
           those directories are searched for all #include directives.

           In addition, -I- inhibits the use of the directory of the
           current file directory as the first search directory for
           "#include "file"".  There is no way to override this effect
           of -I-.

       -Ldir
           Add directory dir to the list of directories to be searched
           for -l.


#链接器选项
   Options for Linking
       These options come into play when the compiler links object files
       into an executable output file.  They are meaningless if the
       compiler is not doing a link step.

       object-file-name
           A file name that does not end in a special recognized suffix
           is considered to name an object file or library.  (Object
           files are distinguished from libraries by the linker
           according to the file contents.)  If linking is done, these
           object files are used as input to the linker.

       -c
       -S
       -E  If any of these options is used, then the linker is not run,
           and object file names should not be used as arguments.


       -llibrary
       -l library
           Search the library named library when linking.  (The second
           alternative with the library as a separate argument is only
           for POSIX compliance and is not recommended.)

           The -l option is passed directly to the linker by GCC.  Refer
           to your linker documentation for exact details.  The general
           description below applies to the GNU linker.

           The linker searches a standard list of directories for the
           library.  The directories searched include several standard
           system directories plus any that you specify with -L.

           Static libraries are archives of object files, and have file
           names like liblibrary.a.  Some targets also support shared
           libraries, which typically have names like liblibrary.so.  If
           both static and shared libraries are found, the linker gives
           preference to linking with the shared library unless the
           -static option is used.

           It makes a difference where in the command you write this
           option; the linker searches and processes libraries and
           object files in the order they are specified.  Thus, foo.o
           -lz bar.o searches library z after file foo.o but before
           bar.o.  If bar.o refers to functions in z, those functions
           may not be loaded.

       -s  Remove all symbol table and relocation information from the
           executable.

       -static
           On systems that support dynamic linking, this overrides -pie
           and prevents linking with the shared libraries.  On other
           systems, this option has no effect.

       -shared
           Produce a shared object which can then be linked with other
           objects to form an executable.  Not all systems support this
           option.  For predictable results, you must also specify the
           same set of options used for compilation (-fpic, -fPIC, or
           model suboptions) when you specify this linker option.[1]
```

## 参考

- [几乎无痛的VSCode+clangd+lldb+cmake配置C/C++开发环境指南](https://zhuanlan.zhihu.com/p/566365173)
- [使用Clangd提升C++代码编写体验](https://zhuanlan.zhihu.com/p/566506467)

