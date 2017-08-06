from conans.model import Generator
from conans import ConanFile, os, tools
# This is the normal packaging info since generators
# get published just like other packages. Although
# most of the standard package methods are overridden
# when there is another class derived from "generator" present.


class BoostGenerator(ConanFile):
    name = "Boost.Generator"
    version = "0.0.1"
    url = "https://github.com/bincrafters/conan-boost-generator"
    description = "Conan build generator for boost libraries http://www.boost.org/doc/libs/1_64_0/libs/libraries.htm"
    license = "BSL"
    boost_version = "1.64.0"
    exports_sources = "boostcpp.jam", "jamroot.template"

# This is the actual generator code


class boost(Generator):
    @property
    def filename(self):
        return "jamroot"

    @property
    def content(self):
        conan_file = self.conanfile
        jam_include_paths = ' '.join('"' + path + '"' for path in conan_file.deps_cpp_info.includedirs)
        boost_build = conan_file.deps_cpp_info["Boost.Build"]
        boost_build_root_path = boost_build.rootpath
        boost_build_kernel_path = os.path.join(boost_build_root_path, "share", "boost-build", "src", "kernel")
        boost_build_jam_content = "boost-build " + boost_build_kernel_path

        boost_generator = conan_file.deps_cpp_info["Boost.Generator"]
        boost_generator_root_path = boost_generator.rootpath
        boost_generator_source_path = os.path.join(boost_generator_root_path, os.pardir, os.pardir, "export_source")
        template_file_path = os.path.join(boost_generator_source_path, "jamroot.template")

        with open("boost-build.jam", "w") as f:
            f.write(boost_build_jam_content)

        with open(template_file_path) as f:
            template_content = f.read()
            jamroot_content = template_content \
                .replace("{{{library}}}", conan_file.lib_short_name) \
                .replace("{{{boost_version}}}", conan_file.version) \
                .replace("{{{deps.include_paths}}}", jam_include_paths) \
                .replace("{{{os}}}", self.b2_os()) \
                .replace("{{{address_model}}}", self.b2_address_model()) \
                .replace("{{{architecture}}}", self.b2_architecture())   \
                .replace("{{{toolset}}}", self.b2_toolset())
            # toolset replace currently does nothing because rene said it should be in cli
            # I don't understand why, so leaving it here until i can ask and make sure
            return jamroot_content

    def b2_os(self):
        b2_os = {
            'Windows': 'target-os=windows',
            'Linux': 'target-os=linux',
            'Macos': 'target-os=darwin',
            'Android': 'target-os=android',
            'iOS': 'target-os=iphone',
            'FreeBSD': 'target-os=freebsd',
            'SunOS': 'target-os=solaris'}
        return b2_os[str(self.settings.os)]

    def b2_address_model(self):
        b2_address_model = {
            'x86': 'address-model=32',
            'x86_64': 'address-model=64',
            'ppc64le': 'address-model=64',
            'ppc64': 'address-model=64',
            'armv6': 'address-model=32',
            'armv7': 'address-model=32',
            'armv7hf': 'address-model=32',
            'armv8': 'address-model=64'}
        return b2_address_model[str(self.settings.arch)]

    def b2_toolset(self):
        b2_toolset = {
            'gcc': 'toolset=gcc',
            'Visual Studio': 'toolset=msvc',
            'clang': 'toolset=clang',
            'apple-clang': 'toolset=darwin'}
        return b2_toolset[str(self.settings.compiler)]

    def b2_architecture(self):
        if str(self.settings.arch).startswith('x86'):
            return 'x86'
        elif str(self.settings.arch).startswith('ppc'):
            return 'power'
        elif str(self.settings.arch).startswith('arm'):
            return 'arm'
        else:
            return ""