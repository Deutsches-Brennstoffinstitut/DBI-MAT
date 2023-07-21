# DBI Microgrid Analysis Toolbox (DBI - MAT)

A powerful techno-economic simulation framework for Power-to-X system analysis, scenario exploration and system
optimization with a focus on flexibility and scalability.

## Folder structure

```  
|-- dbimat              # main program
|  |-- source           # code base
|  |-- templates        # output templates
|-- sphinx              # documentation
|-- test_cases          # examples and tests of different pre build energy systems
|  |-- doc              # documentation
|  |-- notebooks        # jupyter notebooks for system analysis
|  |-- output           # vizuals for test cases
|  |-- source           # test model source code
|  |  |-- systems       # test model systems
requirements.txt        # requirements for the main program
README.md               # this file
```

## CREATE DOCUMENTATION:
Execute the following code in terminal to create the documentation.

 <code>.\sphinx\make html</code>

Code to open the documentation via terminal.
 <code>.\sphinx\build\html\index.html</code>

Or create and open the documentation via Terminal at once.
 <code>.\sphinx\make html ; .\sphinx\build\html\index.html</code>

## License Information:

You are free to:  
- Share
   - copy and redistribute the material in any medium or format
- Adapt
   - remix, transform, and build upon the material
The licensor cannot revoke these freedoms as long as you follow the license terms.

Under the following terms:
- Attribution
  - You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

- NonCommercial
  - You may not use the material for commercial purposes.

- ShareAlike
  - If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

    No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.



## Dependencies
see requirements.txt

## Upcoming:
Examples on how to use the tool and a proper manual. For a first glance see ```test_cases\\notebooks\\testcase_1_sandbox.ipynb```
